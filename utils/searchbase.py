from abc import abstractmethod, ABCMeta

import requests
from django.core.cache import cache

from explorer.models import Favourite
from remoteos.settings import ONLINE_VIDEO_REQUEST_HEADER, ONLINE_VIDEO_BASE_URL, ONLINE_VIDEO_SEARCH_URL

top_floor = 0


class SearchBase:
    # __metaclass__ = ABCMeta

    def __init__(self):
        self.headers = ONLINE_VIDEO_REQUEST_HEADER
        self.base_url = ONLINE_VIDEO_BASE_URL
        self.search_href = ONLINE_VIDEO_SEARCH_URL
        self.xpath_search_dict = {}

    def get(self, url, headers=None):
        full_headers = {}
        if headers is not None:
            full_headers.update(self.headers)
            full_headers.update(headers)
        else:
            full_headers = self.headers

        response_str = requests.get(url=url, headers=full_headers).content.decode()
        return response_str

    def post(self, url, data):
        response_str = requests.post(url=url, data=data, headers=self.headers).content.decode()
        return response_str

    @staticmethod
    def cache_clear(floor=0):
        global top_floor
        print("cache clear ...")
        while True:
            top_floor = 0
            cache.delete(str(floor))
            floor += 1
            if floor > 5:
                # 搜索时的最多层级目前最多只有2层, 这里清理5层确保
                break

    # 默认如下, 可能需要重载
    @abstractmethod
    def search_request(self, keyword):
        pass

    @abstractmethod
    def search_infos_extract(self, search_result):
        # 2. 封面图
        # 3. 标题, 详细分集列表页地址
        # 统计搜索结果数量, 得到element个数 生成序号
        # url列表 , 主要需要缓存, 可不必返回
        # 4. 更新情况, 一共有多少集, 更新完没有的信息使用时格式:  标题(更新情况)
        # 5. 导演	(导演:xxx)
        # 6. 主演	(主演: xxx)
        # 7. 类型	(类型: XXX)
        # 8. 地区	(地区: xxx)
        # 9. 年份	(年份: xxx)
        # 10. 简介	(简介: xxx)
        pass

    def search(self, keyword: str):
        detail_dict = cache.get("0")
        if detail_dict is not None and detail_dict['keyword'] == keyword:
            return detail_dict

        self.cache_clear()

        response_result = self.search_request(keyword)

        detail_dict = self.search_infos_extract(response_result)
        if detail_dict is None:
            return None

        detail_dict["keyword"] = keyword
        detail_dict['floor'] = 0
        cache.set(str(0), detail_dict, timeout=(3600*24))

        print("search result: \n", detail_dict)

        return detail_dict

    @abstractmethod
    def next_floor_request(self, last_floor_dict, index):
        pass

    @abstractmethod
    def next_floor_extract(self, response):
        pass

    def sets_open(self, index, floor):
        global top_floor
        if floor < top_floor:
            next_cache = cache.get(str(floor+1))
            if next_cache['inx'] == index:
                return next_cache
            else:
                self.cache_clear(floor + 1)
                top_floor = floor

        last_cache = cache.get(str(top_floor))
        response = self.next_floor_request(last_cache, index)
        next_dict = self.next_floor_extract(response)

        next_dict['inx'] = index
        next_dict['floor'] = floor + 1
        cache.set(str(floor + 1), next_dict, timeout=(3600 * 24))
        top_floor = floor + 1

        print("next dict: ", next_dict)
        return next_dict

    @staticmethod
    def play(channel, index):
        video_info = cache.get(str(top_floor))
        if video_info is None or video_info['types'][index] == "sets":
            return None

        title = video_info['titles'][index]
        url_link = video_info['urls'][index]
        print("-----------------", title)

        return {'link': url_link, 'name': title}

    def do_select(self, request_dict: dict):
        index = int(request_dict['index'])
        issets = request_dict['type']
        if issets == 'sets':
            report_dict = self.sets_open(int(index), int(request_dict['floor']))
        else:
            report_dict = self.play(int(request_dict['channel']), index)

        return report_dict

    def request_work_start(self, request_dict: dict):
        report_dict = dict()
        if request_dict['action'] == "search":
            report_dict = self.search(request_dict['keyword'])
        elif request_dict['action'] == "select":
            report_dict = self.do_select(request_dict)

        return report_dict

    @staticmethod
    def favor(request_dict: dict):
        print("floor: ", request_dict['floor'], request_dict['index'])

        favor_dict = cache.get(request_dict['floor'])
        if favor_dict is None:
            print("favor_dict is None")
            return
        index = int(request_dict['index'])
        title = favor_dict['titles'][index]
        author = favor_dict['authors'][index]
        url = favor_dict['urls'][index]
        Favourite.objects.create(title=title, author=author, url=url)


SearchBase.cache_clear()















