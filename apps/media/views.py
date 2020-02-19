import json
import socket

# Create your views here.
import struct
import sys

from django.http import HttpResponse
from django.views.generic.base import View

# from celery_tasks import tasks
from explorer.models import TvChannels

g_sock = None
g_media_act = dict()


def verbose_output_clear():
    # 发送查询指令后经常会有多余数据返回, 影响判断所以先执行这个函数清空
    # 稳定性有待考查
    vlc_cmd_request('is_playing')


def cmd_str_construct(func):
    def _deco(act, *args):
        print("before func() called.")

        # [clear, pause, status, get_time, get_length, ...]
        cmd_str = act

        if len(args) >= 0:
            # [add, seek, ...]
            if act == 'add':
                cmd_str = 'add ' + args[0]
            elif act == 'seek' and len(args) == 1:
                cmd_str = 'seek ' + args[0]

        ret_str = func(cmd_str)
        print("after func() called.")
        # 不需要返回func，实际上应返回原函数的返回值
        return ret_str
    return _deco


@cmd_str_construct
def vlc_cmd_request(cmd: str, *args):
    global g_sock
    print("request cmd: ", cmd)
    temp = cmd + '\r'

    try:
        g_sock.sendall(temp.encode())
    except socket.error as msg:
        print(msg)
    else:
        print("sendall exec success")

    resp_str = ""
    i = 0
    while True:
        try:
            i += 1
            resp = g_sock.recv(1024).decode()
        except BlockingIOError as msg:
            break
        else:
            resp_str += resp

    print("vlc cmd[{}]\n recv times[{}]\n recv len[{}]\n response: {}".format(cmd, i, len(resp_str), resp_str))

    return resp_str


def status_get():
    status_dict = dict()
    verbose_output_clear()
    ret = vlc_cmd_request('is_playing').strip('\r\n')
    if ret == '1':
        ret = vlc_cmd_request('play')
        if ret.find("Type 'pause' to continue") >= 0:
            status_dict['status'] = 'pause'
        else:
            status_dict['status'] = 'playing'
    else:
        status_dict['status'] = 'stop'

    verbose_output_clear()
    status_dict['cur_time'] = vlc_cmd_request('get_time').strip('\r\n')
    status_dict['total_time'] = vlc_cmd_request('get_length').strip('\r\n')
    return status_dict


def new_play(full_path):
    ret_str = vlc_cmd_request('play')
    if ret_str.find("Type 'pause' to continue") >= 0:
        vlc_cmd_request('pause')

    vlc_cmd_request('clear')
    vlc_cmd_request('add', full_path)
    return status_get()


def tv_play(tv_id):
    ret_str = vlc_cmd_request('play')
    if ret_str.find("Type 'pause' to continue") >= 0:
        vlc_cmd_request('pause')

    vlc_cmd_request('clear')
    des_channel = TvChannels.objects.filter(channel_id=tv_id)
    if len(des_channel) == 1:
        vlc_cmd_request('add', des_channel[0].channel_url)

    return {'total_time': '2735', 'cur_time': '166', 'uuid': '74f85634ec754c5a96d66925b486af7f', 'status': 'playing'}


def play_ctrl():
    # pause
    vlc_cmd_request('pause')
    return status_get()


def play_handle(request):
    full_path = request.GET.get('path')
    tv_id = request.GET.get('id')
    if full_path is not None:
        full_path = "/media/zjay/Datas" + full_path
        res_dict = new_play(full_path)
    elif tv_id is not None:
        res_dict = tv_play(tv_id)
    else:
        res_dict = play_ctrl()
    return res_dict


def status_handle(request):
    return status_get()


def seek_handle(request):
    progress = request.GET.get('progress')
    print("progress type: ", type(progress))
    if progress is None:
        progress = '0'

    vlc_cmd_request('seek', progress)
    return status_get()


def stop_handle(request):
    print(sys._getframe().f_code.co_name)
    pass


def socket_init():
    global g_sock
    print("socket_init start")
    try:
        g_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        g_sock.connect("/home/zjay/vlc.sock")
        val = struct.pack("QQ", 0, 10 * 1000)
        g_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)
        print("socket init ok")
    except socket.error as msg:
        print("unix socket create failed", msg)


def action_init():
    print("action_init start")
    global g_media_act
    g_media_act['play'] = play_handle
    g_media_act['status'] = status_handle
    g_media_act['seek'] = seek_handle
    g_media_act['stop'] = stop_handle


def media_init():
    socket_init()
    action_init()


media_init()


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


