from lxml import etree

from utils.basespider import BaseSpider
from celery_tasks import tasks


class SuyingSpider(BaseSpider):
    def __init__(self):
        BaseSpider.__init__(self)
        self.xpath_search_dict = {
            "covers": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[1]/a/@data-original",
            "titles": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/h3/a/text()",
            "hrefs": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/h3/a/@href",
            "status": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[1]/a/span[2]/text()",
            "directors": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/p[1]/a/text()",
            "actors": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/p[2]/text()",
            "types": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/p[3]/text()[1]",
            "areas": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/p[3]/text()[2]",
            "date": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/p[3]/span[4]/text()",
            "description": "/html/body/div[2]/div/div[1]/div/div/div[2]/ul/li/div[2]/p[4]/text()"
        }

        self.xpath_playlist_dict = {
            # "main_title": "/html/body/div[2]/div/div[1]/div/div/div[1]/div/div[2]/h3/text()",
            "sub_titles": "/html/body/div[2]/div/div[2]/div/div[2]/ul/li/a/text()",
            "sub_href": "/html/body/div[2]/div/div[2]/div/div[2]/ul/li/a/@href",
        }

    def search_infos_extract(self, search_result):
        result_element = etree.HTML(search_result)

        res_dict = {}
        for (key, val) in self.xpath_search_dict.items():
            res_dict[key] = result_element.xpath(self.xpath_search_dict[key])

        res_dict["indexes"] = [i for i in range(len(res_dict["titles"]))]
        return res_dict

    def playlist_infos_extract(self, playlist_result):
        result_element = etree.HTML(playlist_result)
        playlist_dict = {'titles': result_element.xpath(self.xpath_playlist_dict["sub_titles"]),
                         "hrefs": result_element.xpath(self.xpath_playlist_dict["sub_href"])}

        playlist_dict['indexes'] = [i for i in range(len(playlist_dict['titles']))]
        return playlist_dict

    def playlist_request(self, search_dict, index):
        playlist_href = search_dict['hrefs'][index]
        return self.get(self.base_url + playlist_href)

    def playurl_list_request(self, playlist_dict, index):
        tasks.real_playlist_request.delay(playlist_dict["hrefs"][0], index)

    def search_request(self, keyword):
        print("suying search request")
        data = {"wd": keyword}
        return self.post(self.base_url + self.search_href, data)
