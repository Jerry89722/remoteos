import json
import os
import socket
import sys
import threading

from django.core.cache import cache
from django.http import HttpResponse
from django.views.generic.base import View
from explorer.models import TvChannels
from explorer.views import file_list_get, real_path_get

from celery_tasks.tasks import isCelery
from remoteos.settings import VLC_SOCK_PATH, DISK_PATH
from utils.socketmanager.unixsocketmanager import UnixSocketManager

g_sock = None
g_sock_lock = None
g_media_act = dict()


def cmd_str_construct(func):
    def _deco(act, *args):
        # [clear, pause, status, get_time, get_length, ...]
        cmd_str = ""

        if len(args) > 0:
            # [add, seek, ...]
            if act == 'add':
                cmd_str = 'add ' + args[0]
            elif act == 'seek':
                cmd_str = 'seek ' + args[0]
            elif act == 'volume':
                cmd_str = 'volume ' + args[0]
            elif act == 'volup':
                cmd_str = 'volup ' + args[0]
            elif act == 'voldown':
                cmd_str = 'voldown ' + args[0]
            else:
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

    print("sent: ", temp)
    resp = ""
    try:
        resp = g_sock.recv(1024).decode()
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
    # path = vlc_cmd_request('status').strip('\r\n')
    # from urllib import parse
    # path = parse.unquote(path)
    # if path.find("file://") == 0:
    #     title = path[path.rfind('/') + 1:]
    # elif path.find("http") == 0 and path.rfind("m3u8") > 0:
    #     des_channel = TvChannels.objects.filter(channel_url=path)[0]
    #     title = des_channel.channel_name
    # else:
    #     title = vlc_cmd_request('get_title').strip('\r\n')
    #
    # print("path", path)
    playing_info = cache.get("player_status_cache")
    title = playing_info['name']
    print("title", title)
    return title


def all_status_get():
    status_dict = dict()
    verbose_output_clear()
    status_dict['status'] = get_status()
    if status_dict['status'] == 'stop':
        player_status_dict = cache.get('player_status_cache')
        if player_status_dict is not None:
            status_dict['name'] = player_status_dict.get('name')
        else:
            status_dict['name'] = ""
    else:
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


# if res is None:
    #     print("play list: \n", playlist)
    #     print("media name: ", media_name)
    # else:
    #     inx = res.group(1)
    #
    #     print("play index: ", inx)
    #
    #     vlc_cmd_request('goto', inx)


def media_switch(mtype, full_path):
    if get_status() == 'pause':
        vlc_cmd_request('pause')
    vlc_cmd_request('stop')
    vlc_cmd_request('clear')
    if mtype == 'tv':
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
    # pause
    vlc_cmd_request('pause')

    return all_status_get()


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


def play_handle(request):
    media_type = request.GET.get('type')
    full_path = request.GET.get('fingerprint')
    print("media type: ", media_type)
    print("full path: ", full_path)
    if all([full_path, media_type]):
        chan = None
        if media_type == 'tv':
            chan = TvChannels.objects.filter(channel_id=full_path)[0]
            full_path = chan.channel_url
        elif media_type == 'video' or media_type == 'audio':
            full_path = DISK_PATH + full_path

        media_switch(media_type, full_path)
        player_status_cache = {'path': full_path, 'type': media_type}
        if media_type == 'tv':
            player_status_cache['name'] = chan.channel_name
        elif media_type == 'internet':
            player_status_cache['name'] = request.GET.get('name')
        else:
            player_status_cache['name'] = full_path[full_path.rfind('/')+1:]

        cache.set("player_status_cache", player_status_cache, timeout=(24*3600))
    else:
        # 暂停/播放当前任务
        if get_status() == 'stop':
            player_status_dict = cache.get("player_status_cache")
            if player_status_dict is not None:
                if player_status_dict.get('path') is not None:
                    media_switch(player_status_dict['type'], player_status_dict['path'])

        play_ctrl()

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


def action_init():
    print("action_init start")
    global g_media_act
    g_media_act['play'] = play_handle
    g_media_act['status'] = status_handle
    g_media_act['seek'] = seek_handle
    g_media_act['stop'] = stop_handle
    g_media_act['volume'] = volume_handle


def socket_init():
    global g_sock
    global g_sock_lock
    print("socket_init start")
    g_sock_lock = threading.Lock()
    g_sock = UnixSocketManager()

    # try:
    #     g_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    #     g_sock.connect(VLC_SOCK_PATH)
    #     # val = struct.pack("QQ", 0, 10 * 1000)
    #     # g_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)
    #     print("socket init ok")
    # except socket.error as msg:
    #     print("unix socket create failed", msg)


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


