import threading
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote


class SimulateBrowser:
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(SimulateBrowser, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def __init__(self):
        if self.__first_init is True:
            self.__first_init = False
            print("simulate browser init")
            # chrome_options = Options()
            # chrome_options.add_argument('--headless')
            # self.browser = webdriver.Chrome(chrome_options=chrome_options)     # 创建Chrome对象
            self.browser = webdriver.Chrome()
            self.wait_task = threading.Event()
            self.wait_response = threading.Event()
            self.task_thread = threading.Thread(target=self.working_thread)
            self.task_thread.start()
            self.request_dict = dict()
            self.response_dict = dict()
            self.channel_list = []
            self.link = ""

    def goto_index(self):
        print("simulate browser open")
        self.browser.get('https://wap.dadatu5.com/')
        print("simulate browser open done")

    def working_thread(self):
        self.goto_index()
        while True:
            self.wait_task.wait()
            self.wait_task.clear()
            self.do_work()

    def do_work(self):
        print("get work: ", self.request_dict)
        # work handle
        ret = self.work_handle()

        self.work_report_set(ret)

    def request_work_start(self, request_dict: dict):
        # self.request_dict = {"action": "search", "keyword": "庆余年"}
        # self.request_dict.clear()
        self.request_dict = request_dict
        self.wait_task.set()
        self.wait_response.wait()
        self.wait_response.clear()
        return self.response_dict

    def work_report_set(self, reporter: dict):
        # self.request_dict.clear()
        self.response_dict = reporter
        self.wait_response.set()

    def work_handle(self):
        report_dict = dict()
        if self.request_dict['action'] == "search":
            report_dict = self.search(self.request_dict['keyword'])
        elif self.request_dict['action'] == "info":
            report_dict = self.details(int(self.request_dict['index']))
        elif self.request_dict['action'] == "play":
            report_dict = self.video_link(int(self.request_dict['channel']), int(self.request_dict['index']))

        return report_dict

    def search(self, keyword):
        ret_dict = {'list': []}
        self.browser.find_element_by_id('wd').clear()
        self.browser.find_element_by_id('wd').send_keys(keyword)
        self.browser.find_element_by_id('searchbutton').click()
        results = self.browser.find_elements_by_xpath("//ul/li/div/h3/a")
        print("search result[{}]: {}".format(len(results), results))
        i = 0
        for element in results:
            ret_dict['list'].append({'title': element.text, 'index': i, 'type': "internet"})
            i += 1
        '''
            {
                "uuid": "uuid",
                "list": [{"title": "庆余年", "index": "1"}, {"title": "庆余年", "index": "2"}]
            }
        '''
        return ret_dict

    def details(self, index: int):
        ret_dict = {'list': []}
        details_btn = self.browser.find_elements_by_xpath("//ul/li/div/p/a[contains(@class, 'btn btn-min btn-default')]")
        details_btn[index].click()
        self.channel_list = self.browser.find_elements_by_class_name("playlist")

        i = 0
        for channel in self.channel_list:
            channel_dict = {"channel": "线路{}".format(i), "index": str(i), "list": []}
            video_list = channel.find_elements_by_xpath("./ul/li/a")
            channel_dict['list'] = [str(x) for x in range(len(video_list))]
            ret_dict['list'].append(channel_dict)
            i += 1
        '''
        {
        "uuid": "uuid",
        "list": [{
            "channel": "腾讯视频",
            "index": "0",
            "list": ["1", "2", "3"]
        }, {
            "channel": "云快视频",
            "index": "1",
            "list": ["1", "2", "3"]
        }, {
            "channel": "云播视频",
            "index": "2",
            "list": ["1", "2", "3"]
        }]
        }
        '''
        return ret_dict

    def video_link(self, channel, which):
        # self.video_list[index].click()
        play_list = self.channel_list[channel].find_elements_by_xpath("./ul/li/a")
        print("playlist element detail: ", play_list[which].__str__())
        play_list[which].click()

        # driver.switch_to.default_content()
        frame = self.browser.find_elements_by_xpath('//table/tbody/tr/td/iframe')[0]
        print("iframe src: ", frame.get_attribute('src'))
        self.browser.switch_to.frame(frame)
        locator = (By.XPATH, '//video')

        try:
            WebDriverWait(self.browser, 20, 0.5).until(EC.presence_of_element_located(locator))
            video = self.browser.find_element_by_xpath("//video")
        finally:
            print("wait done")
            # self.browser.close()

        print("video element details", video.__str__())

        self.link = video.get_attribute('src')
        if self.link is not None:
            self.browser.switch_to.default_content()
            self.browser.back()
        print("video src: ", self.link)

        self.link = quote(self.link, 'utf-8')
        print("video src: ", self.link)

        return {"link": self.link}

    '''
        # work report
        self.work_report({
            "uuid": "uuid",
            "list": [{"name": "庆余年", "index": "1"}, {"name": "庆余年", "index": "2"}]
        })  # 查找的结果

        self.work_report({
            "uuid": "uuid",
            "list": [["1", "2", "3"], ["1", "2", "3"]]
        })  # 分集结果

        self.work_report({"uuid": "uuid"})  # 分析出播放链接后的返回
    '''



