import collections
import json


from utils.searchbase import SearchBase


class MusicSearchSpider(SearchBase):

    def __init__(self):
        SearchBase.__init__(self)
        self.base_url = "https://yinyue.lkxin.cn/"
        self.search_href = ""
        self.headers["X-Requested-With"] = "XMLHttpRequest"

    def search_infos_extract(self, search_result):
        res_dict = {"titles": [], "urls": [], "authors": [], "types": [], "covers": []}

        print("crazy music search result: \n", search_result)
        response_dict = json.loads(search_result)
        print("crazy music search result code: \n", response_dict["code"])
        if response_dict["code"] != 200:
            return None
        data_list = response_dict['data']
        for data in data_list:
            res_dict['titles'].append(data['title'] + "-" + data['author'])
            # http://music.163.com/#/song?id=531295576
            id = data['link'].split('=')[-1]
            url = "http://music.163.com/song/media/outer/url?id={}.mp3".format(id)
            res_dict['urls'].append(url)
            res_dict['authors'].append(data['author'])
            res_dict['covers'].append(data['pic'])
            res_dict['types'].append('music')

        res_dict['indexes'] = [i for i in range(len(res_dict['titles']))]

        print("result dict: ", res_dict)
        return res_dict

    def search_request(self, keyword):
        print("crazy music search request")
        data = {
            "input": keyword,
            "filter": "name",
            "type": "netease",
            "page": "1"
        }

        return self.post(self.base_url + self.search_href, data)

    def next_floor_request(self, last_floor_dict, index):
        pass

    def next_floor_extract(self, response):
        pass

