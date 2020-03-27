import json
import os
import filetype

from django.http import HttpResponse
from django.shortcuts import redirect
from explorer.models import TvChannels
from django.views.generic.base import View
from explorer.niuniutv import NiuNiuTvSpider
from remoteos.settings import DISK_PATH


def real_path_get(vpath):
    return DISK_PATH + vpath


def file_list_get(file_type, full_path):
    result = list()
    type_list = file_type.split('/')
    # print("type list: ", type_list)
    for name in os.listdir(full_path):
        item = dict()
        item_path = full_path + "/" + name
        print("--------------", item_path)

        if os.path.isdir(item_path):
            item['type'] = 'dir'
            item['name'] = name
            item['fingerprint'] = item_path.replace(DISK_PATH, "", 1)
        else:
            ftype = filetype.guess(item_path)
            if ftype is None:
                continue

            ft = ftype.mime.split('/')[0]
            if file_type == 'all' or ft in type_list:
                item['type'] = ft
                item['name'] = name
                item['fingerprint'] = item_path.replace(DISK_PATH, "", 1)
            else:
                item['type'] = ft
                item['name'] = name
                item['fingerprint'] = item_path.replace(DISK_PATH, "", 1)

            item['size'] = str(os.path.getsize(item_path))

        result.append(item)
    return result


def online_video_list_get():
    return []


def tv_list_get():
    channel_list = TvChannels.objects.all().order_by('channel_id')
    print("channel_list type: ", type(channel_list))
    print("channel_list: ", channel_list)
    channels = []
    for channel in channel_list:
        channel_dict = dict()
        channel_dict["name"] = channel.channel_name
        channel_dict["fingerprint"] = str(channel.channel_id)
        channel_dict["id"] = channel.channel_id
        channel_dict["type"] = "tv"
        channel_dict["size"] = "0"
        channels.append(channel_dict)

    return channels


def list_handle(request):
    file_type = request.GET.get('type')
    file_path = request.GET.get('fingerprint')

    if file_type == 'tv':
        res_list = tv_list_get()
    else:
        full_path = DISK_PATH + ("" if file_path == "/" else file_path)
        print("explorer full path: ", full_path)
        res_list = file_list_get(file_type, full_path)

    return res_list


def rm_handle():
    pass


def explorer_env_init():
    print("explorer env init")
    global g_explorer_act, sim
    if sim is None:
        g_explorer_act['list'] = list_handle
        g_explorer_act['rm'] = rm_handle
        # sim = SimulateBrowser()


sim = None
g_explorer_act = dict()

explorer_env_init()


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


class InternetView(View):
    """
    def get(self, request):
        global sim
        response_dict = sim.request_work_start(request.GET)
        print("internet task response: ", response_dict)
        if 'link' in response_dict:
            print("internet video url: ", response_dict['link'])
            return redirect("/media?action=play&type=internet&fingerprint={}".format(response_dict['link']))

        return HttpResponse(json.dumps(response_dict))

    def post(self, request):
        pass
    """

    def get(self, request):
        # searcher = SuyingSpider()
        searcher = NiuNiuTvSpider()
        response_dict = searcher.request_work_start(request.GET)
        if response_dict is None:
            response = HttpResponse()
            response.status_code = 404
            response.content = "无结果"
            return response
        if 'link' in response_dict:
            print("internet video url: ", response_dict['link'])
            return redirect("/media?action=play&type=internet&name={}&fingerprint={}".format(response_dict['name'], response_dict['link']))

        return HttpResponse(json.dumps(response_dict))








