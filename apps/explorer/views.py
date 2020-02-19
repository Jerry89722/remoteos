import json
import logging
import os

from django.http import HttpResponse
from explorer.models import TvChannels

# Create your views here.
from django.views.generic.base import View
import filetype

# from apps.explorer.models import TvChannels


def file_list_get(file_type, full_path):
    result = list()
    for name in os.listdir(full_path):
        item = dict()
        item_path = full_path + name
        print("--------------", item_path)
        if os.path.isdir(item_path):
            item['type'] = 'dir'
        else:

            ftype = filetype.guess(item_path)

            if ftype is None:
                item['type'] = 'file'
            else:
                type_src = ftype.mime
                if type_src.find('video') == 0:
                    item['type'] = 'video'
                elif type_src.find('audio'):
                    item['type'] = 'audio'
                else:
                    item['type'] = 'file'
            item['size'] = str(os.path.getsize(item_path))
        item['name'] = name
        print("item", name)
        result.append(item)
    return result


def online_video_list_get():
    return []


def tv_list_get():
    channel_list = TvChannels.objects.all()
    print("channel_list type: ", type(channel_list))
    print("channel_list: ", channel_list)
    channels = []
    for channel in channel_list:
        channel_dict = dict()
        channel_dict["name"] = channel.channel_name
        channel_dict["id"] = channel.channel_id
        channel_dict["type"] = "tv"
        channels.append(channel_dict)

    return channels


def list_handle(request):
    file_type = request.GET.get('type')
    file_path = request.GET.get('path')
    if file_path is None:
        res_list = None
    elif file_path == 'internet':
        if file_type == 'tv':
            res_list = tv_list_get()
        else:
            res_list = online_video_list_get()
    else:
        # local path
        full_path = "/media/zjay/Datas" + file_path
        print("explorer full path: ", full_path)
        res_list = file_list_get(file_type, full_path)

    return res_list


def rm_handle():
    pass


def explorer_action_init():
    global g_explorer_act
    g_explorer_act['list'] = list_handle
    g_explorer_act['rm'] = rm_handle


g_explorer_act = dict()
explorer_action_init()


class FileView(View):

    def get(self, request):
        global g_explorer_act
        uuid = request.GET.get('uuid')
        action = request.GET.get('action')

        res_list = g_explorer_act[action](request)

        response_dict = {'uuid': uuid, 'list': res_list}
        print("file view response: ", response_dict)
        return HttpResponse(json.dumps(response_dict))

    def post(self, request):
        pass


class MusicView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class DocView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class VideoView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass

