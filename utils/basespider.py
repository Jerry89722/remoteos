from abc import abstractmethod, ABCMeta

import requests
from django.core.cache import cache

from remoteos.settings import ONLINE_VIDEO_REQUEST_HEADER, ONLINE_VIDEO_BASE_URL, ONLINE_VIDEO_SEARCH_URL


class BaseSpider:
    # __metaclass__ = ABCMeta

    def __init__(self):
        self.__headers = ONLINE_VIDEO_REQUEST_HEADER
        self.base_url = ONLINE_VIDEO_BASE_URL
        self.search_href = ONLINE_VIDEO_SEARCH_URL
        self.xpath_search_dict = {}

    def get(self, url, headers=None):
        full_headers = {}
        if headers is not None:
            full_headers.update(self.__headers)
            full_headers.update(headers)
        else:
            full_headers = self.__headers

        response_str = requests.get(url=url, headers=full_headers).content.decode()
        return response_str

    def post(self, url, data):
        response_str = requests.post(url=url, data=data, headers=self.__headers).content.decode()
        return response_str

    @staticmethod
    def cache_clear():
        print("cache clear ...")
        cache.delete("search_result_cache")
        cache.delete("playlist_result_cache")
        cache.delete("playlist_urls_result_cache")

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
        detail_dict = cache.get("search_result_cache")
        if detail_dict is not None and detail_dict['keyword'] == keyword:
            return detail_dict

        self.cache_clear()

        response_result = self.search_request(keyword)

        detail_dict = self.search_infos_extract(response_result)
        if detail_dict is None:
            return None
        detail_dict["keyword"] = keyword

        cache.set("search_result_cache", detail_dict, timeout=(3600*24))

        print("search result: \n", detail_dict)

        return detail_dict

    @abstractmethod
    def playurl_list_request(self, playlist_dict, index):
        pass

    @abstractmethod
    def playlist_request(self, search_dict, index):
        pass

    def playlist_info_get(self):
        pass

    def playlist_infos_extract(self, search_result):
        return {}

    def detail(self, index: int):
        """
            点击搜索列表后 获取其中某一项的播放列表页面
        """
        playlist_dict = cache.get("playlist_result_cache")
        if playlist_dict is not None and playlist_dict['inx'] == index:
            playlist_urls = cache.get("playlist_urls_result_cache")
            if playlist_urls is None or playlist_urls['inx'] != index:
                self.playurl_list_request(playlist_dict, index)
            return playlist_dict

        cache.delete("playlist_result_cache")
        cache.delete("playlist_urls_result_cache")

        search_dict = cache.get("search_result_cache")
        main_title = search_dict["titles"][index]

        playlist_result = self.playlist_request(search_dict, index)

        playlist_dict = self.playlist_infos_extract(playlist_result)
        playlist_dict["num"] = str(index)
        playlist_dict['inx'] = index
        playlist_dict["main_title"] = main_title

        cache.set("playlist_result_cache", playlist_dict, timeout=(3600*24))

        # 此操作可能在获取到视频列表后, 再发送一次请求获取播放链接列表,
        # 这种情况时子类中重载实现为celery异步请求, 以提高视频列表的展示速度
        self.playurl_list_request(playlist_dict, index)

        # tasks.real_playlist_request.delay(video_hrefs[0], index)

        print("playlist result: \n", playlist_dict)

        return playlist_dict

    @staticmethod
    def play(channel, index):
        video_info = cache.get("playlist_result_cache")
        main_title = video_info['main_title']
        subtitle = video_info['titles'][index]
        title = "{}-{}".format(main_title, subtitle)
        print("-----------------", main_title)
        print("-----------------", title)
        print("-----------------", subtitle)
        playlist = cache.get("playlist_urls_result_cache")
        print("------------- playlist urls get result: \n", playlist["playlist_urls"])
        if playlist is not None:
            print("video link: ", playlist["playlist_urls"][index])
            return {'link': playlist["playlist_urls"][index], 'name': title}
        return None

    def request_work_start(self, request_dict: dict):
        report_dict = dict()
        if request_dict['action'] == "search":
            report_dict = self.search(request_dict['keyword'])
        elif request_dict['action'] == "info":
            report_dict = self.detail(int(request_dict['index']))
        elif request_dict['action'] == "play":
            report_dict = self.play(int(request_dict['channel']), int(request_dict['index']))

        return report_dict


BaseSpider.cache_clear()















