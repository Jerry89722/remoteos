import collections
import json

from django.core.cache import cache
from utils.searchbase import SearchBase


class NiuNiuTvSpider(SearchBase):
    def __init__(self):
        SearchBase.__init__(self)

    def search_infos_extract(self, search_result):
        # result = search_result.text
        print("search result: ", search_result)
        response_dict = json.loads(search_result, object_pairs_hook=collections.OrderedDict)
        if response_dict['status'] != 200:
            return None
        resource_dict = response_dict['res']
        # resource_dict = response_dict['res']
        print("resouce dict: \n", resource_dict)

        result_dict = {"titles": [], "urls": [], "types": []}

        for (key, val) in resource_dict.items():
            print("key: ", key)
            print("val: ", val)
            result_dict["titles"].append(key)
            result_dict["urls"].append(val)
            result_dict["types"].append('sets')

        null_list = ["none" for i in range(len(result_dict["titles"]))]
        result_dict["authors"] = null_list

        result_dict["covers"] = null_list
        result_dict["status"] = null_list
        result_dict["directors"] = null_list
        result_dict["actors"] = null_list
        result_dict["areas"] = null_list
        result_dict["date"] = null_list
        result_dict["description"] = null_list
        result_dict["indexes"] = [i for i in range(len(result_dict["titles"]))]

        return result_dict

    def next_floor_request(self, last_floor_dict, index):
        return self.playlist_request(last_floor_dict, index)

    def next_floor_extract(self, response):
        return self.playlist_infos_extract(response)

    def playlist_infos_extract(self, playlist_result):
        # result = playlist_result.text
        print("-----------------: \n", playlist_result)
        response_dict = json.loads(playlist_result, object_pairs_hook=collections.OrderedDict)
        # resource_dict = response_dict['res']
        resource_dict = response_dict['res']
        print("resource dict: ", resource_dict)
        # 分集标题
        # 分集href
        playlist_dict = {'titles': [],
                         "urls": [],
                         "types": [],
                         "covers": []}
        for (title, href) in resource_dict.items():
            playlist_dict['titles'].append(title)
            playlist_dict['urls'].append(href[15:])
            playlist_dict['covers'].append("none")
            playlist_dict['types'].append("video")

        playlist_dict['indexes'] = [i for i in range(len(playlist_dict['titles']))]

        print("niu niu playlist: ", playlist_dict)
        return playlist_dict

    def playlist_request(self, search_dict, index):
        playlist_num = search_dict['urls'][index]
        header_extra = {"Referer": "http://ziliao6.com/tv/"}
        return self.get(self.base_url + self.search_href.format("play", playlist_num), headers=header_extra)

    def playurl_list_request(self, playlist_dict, index):
        playlist_urls_dict = cache.get("playlist_urls_result_cache")
        if playlist_urls_dict is not None:
            return

        playlist_urls = playlist_dict["hrefs"]

        cache.set("playlist_urls_result_cache", {"playlist_urls": playlist_urls, "inx": index}, timeout=(3600 * 24))

        print("playlist urls result: \n", playlist_urls)

    def search_request(self, keyword):
        print("niuniu tv search request: ", self.base_url + self.search_href.format("get", keyword))
        header_extra = {"Referer": "http://ziliao6.com/tv/"}
        return self.get(self.base_url + self.search_href.format("get", keyword), headers=header_extra)

