import json
import os
import socket
import sys
import threading
import time

from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic.base import View
from explorer.models import TvChannels, Favourite
from explorer.views import file_list_get, real_path_get

from celery_tasks.tasks import isCelery
from remoteos.settings import VLC_SOCK_PATH, DISK_PATH, VLC_PLAYING_PATH
from utils.socketmanager.unixsocketmanager import UnixSocketManager

g_sock = None
g_sock_lock = None
g_media_act = dict()


class MediaItem:
    def __init__(self, title, url):
        self.title = title
        self.url = url


def cmd_str_construct(func):
    def _deco(act, *args):
        if len(args) > 0:
            cmd_str = act + " " + args[0]
        else:
            cmd_str = act

        ret_str = func(cmd_str)
        # print("after func() called.")
        # 不需要返回func，实际上应返回原函数的返回值
        return ret_str
    return _deco


@cmd_str_construct
def vlc_cmd_request(cmd: str, *args):
    global g_sock
    global g_sock_lock
    temp = cmd + '\r'
    g_sock_lock.acquire(5)
    try:
        g_sock.sendall(temp.encode())
    except socket.error as msg:
        print(msg)

    print("vlc cmd[{}]".format(cmd))

    resp = ""
    try:
        print("recv waiting ...")
        resp = g_sock.recv(1024).decode()
        print("recv done.")
    except BlockingIOError as msg:
        print("blocking io error: ", msg)
    g_sock_lock.release()
    print("vlc cmd[{}]\n recv len[{}]\n response: [{}]".format(cmd, len(resp), resp))

    return resp


def verbose_output_clear():
    # 发送查询指令后经常会有多余数据返回, 影响判断所以先执行这个函数清空
    # 稳定性有待考查
    vlc_cmd_request('is_playing')


def get_status():
    ret = vlc_cmd_request('is_playing').strip('\r\n')
    if ret == '1':
        ret = vlc_cmd_request('play')
        if ret.find("Type 'pause' to continue") >= 0:
            return 'pause'
        else:
            return 'playing'
    else:
        return 'stop'


def get_time():
    return vlc_cmd_request('get_time').strip('\r\n')


def get_length():
    return vlc_cmd_request('get_length').strip('\r\n')


def get_volume():
    return vlc_cmd_request('volume').strip('\r\n')


def get_title():
    playlist = cache.get('playlist')
    time.sleep(0.1)
    with open(VLC_PLAYING_PATH, 'r') as fp:
        ret = fp.read()
    title = playlist['title'][int(ret)]
    print("current item: ", title)
    return title


def all_status_get():
    status_dict = dict()
    # verbose_output_clear()
    status_dict['status'] = get_status()

    status_dict["name"] = get_title()

    status_dict['cur_time'] = get_time()
    status_dict['total_time'] = get_length()
    status_dict['volume'] = get_volume()
    return status_dict


def media_play(media_name):
    playlist = vlc_cmd_request('playlist')
    # res = re.match(r'.* *(\d+) *- *(%s) *\(.*:(\d*)\).*' % media_name, playlist)
    # res = re.match(r'.*(\d+).*(%s).*' % media_name, playlist)
    res = playlist.split('\r\n|')[1:-1]
    print("list results: ", res)
    if len(res) == 0:
        return
    inx = res.index("  - " + media_name)
    print("play index: ", inx)

    vlc_cmd_request('goto', str(inx+1))


def media_switch(mtype, full_path):
    if get_status() == 'pause':
        vlc_cmd_request('pause')
    vlc_cmd_request('stop')
    vlc_cmd_request('clear')
    if mtype == 'tv':
        vlc_cmd_request('add', full_path)
        return
    if mtype == 'favor':
        vlc_cmd_request('add', full_path)
        return
    if mtype == 'internet':
        vlc_cmd_request('add', full_path)
        return

    file_tuple = os.path.split(full_path)

    media_list = file_list_get('video', file_tuple[0]+'/')
    for media in media_list:
        vlc_cmd_request('enqueue', real_path_get(media['fingerprint']))

    media_play(file_tuple[1])


def play_ctrl():
    status = get_status()
    if status == "stop":
        vlc_cmd_request('play')
    elif status == 'pause':
        vlc_cmd_request('pause')
    else:
        vlc_cmd_request('pause')


def volume_ctrl(vol):
    vol_int = vol
    if vol > 0:
        cur_vol = vlc_cmd_request("volume").strip('\r\n')
        print("cur vol: {}-".format(cur_vol))
        if cur_vol == "0":
            vlc_cmd_request("volume", "1")

        act = "volup"
    elif vol < 0:
        act = "voldown"
    else:
        act = "volume"

    vol_str = str(abs(vol_int))

    vlc_cmd_request(act, vol_str)

    return all_status_get()


def do_play(item):
    if item is None:
        # 播放第一首
        pass
    else:
        playlist = cache.get('playlist')
        print('get playlist: ', playlist)
        print("cur_item: ", item)
        index = playlist['url'].index(item['url'])
        vlc_cmd_request('goto', str(index + 1))


def playlist_update(media_type, fingerprint, name=None):
    playlist = {
        'type': 'tv',
        'title': [],
        'url': []
    }

    item_list = []
    cur_item = {
        "title": None,
        "url": None
    }
    if media_type == 'tv':
        cur_item = TvChannels.objects.filter(item_number=fingerprint)[0]
        cur_item = {
            'title': cur_item.title,
            'url': cur_item.url
        }
        item_list = TvChannels.objects.all()
    elif media_type == 'video' or media_type == 'audio':
        cur_url = DISK_PATH + fingerprint
        cur_item = {
            'title': fingerprint.split('/')[-1],
            'url': cur_url
        }
        item_list = [MediaItem(fingerprint.split('/')[-1], cur_url)]
    elif media_type == 'favor':
        cur_item = Favourite.objects.filter(id=fingerprint)[0]
        cur_item = {
            'title': cur_item.title,
            'url': cur_item.url
        }
        # db_items = Favourite.objects.filter(~Q(id=full_path))
        item_list = Favourite.objects.all()
    elif media_type == 'internet':
        cur_item = {'title': name, 'url': fingerprint}
        item_list = [MediaItem(name, fingerprint)]

    vlc_cmd_request("stop")
    vlc_cmd_request("clear")

    for item in item_list:
        print("title: ", item.title)
        print("url: ", item.url)
        playlist['title'].append(item.title)
        playlist['url'].append(item.url)
        vlc_cmd_request("enqueue", item.url)
    print("full playlist: ", playlist)
    cache.set('playlist', playlist, timeout=(24*3600))

    return cur_item


def play_handle(request):
    media_type = request.GET.get('type')
    fingerprint = request.GET.get('fingerprint')
    name = request.GET.get('name')

    if fingerprint is None:
        # 仅切换播放/暂停状态
        play_ctrl()
    else:
        # 播放新节目
        cur = playlist_update(media_type, fingerprint, name)
        do_play(cur)

    return all_status_get()


def volume_handle(request):
    res_dict = {}

    volume = request.GET.get('volume')
    if volume is not None:
        vol = int(volume)
        res_dict = volume_ctrl(vol)
    return res_dict


def status_handle(request):
    return all_status_get()


def seek_handle(request):
    progress = request.GET.get('progress')
    print("progress type: ", type(progress))
    if progress is None:
        progress = '0'

    vlc_cmd_request('seek', progress)
    return all_status_get()


def stop_handle(request):
    print(sys._getframe().f_code.co_name)

    if get_status() == 'pause':
        vlc_cmd_request('pause')
    vlc_cmd_request('stop')

    return all_status_get()


def next_handle(request):
    status = get_status()
    if status == 'pause':
        vlc_cmd_request('pause')
    vlc_cmd_request('next')
    print("next handle")
    vlc_cmd_request('playlist')
    return all_status_get()


def prev_handle(request):
    status = get_status()
    if status == 'pause':
        vlc_cmd_request('pause')
    vlc_cmd_request('prev')
    print("prev handle")
    return all_status_get()


def random_handle(request):
    vlc_cmd_request('random', request.GET.get('onoff'))
    return all_status_get()


def action_init():
    print("action_init start")
    global g_media_act
    g_media_act['play'] = play_handle
    g_media_act['status'] = status_handle
    g_media_act['seek'] = seek_handle
    g_media_act['stop'] = stop_handle
    g_media_act['volume'] = volume_handle
    g_media_act['next'] = next_handle
    g_media_act['prev'] = prev_handle
    g_media_act['random'] = random_handle


def socket_init():
    global g_sock
    global g_sock_lock
    print("socket_init start")
    g_sock_lock = threading.Lock()
    g_sock = UnixSocketManager()


def media_init():
    socket_init()
    action_init()


if isCelery is False:
    print("---------- media init ----------")
    media_init()


# name, location, type
class MediaView(View):
    def __init__(self):
        super(MediaView, self).__init__()
        print("MediaView init ... ")

    def get(self, request):
        global g_media_act
        uuid = request.GET.get('uuid')
        action = request.GET.get('action')
        res_dict = g_media_act[action](request)

        res_dict['uuid'] = uuid
        print("media view response: ", res_dict)
        return HttpResponse(json.dumps(res_dict))

    def post(self, request):
        act = request.POST.get('action')
        if act is not None:
            return HttpResponse('200')
        else:
            return HttpResponse('501')


print("line num: ", sys._getframe().f_lineno)


