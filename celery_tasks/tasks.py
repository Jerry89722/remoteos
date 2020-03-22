"""
启动命令: celery -A celery_tasks.tasks worker -l info
"""
import re
import time
import os
import requests

from urllib.parse import unquote
from celery import Celery
from django.core.cache import cache
from lxml import etree
from remoteos import settings
from django.core.mail import send_mail
from remoteos.settings import DEVICE_UUID, PUBLIC_DOMAIN

if os.environ.get('DJANGO_SETTINGS_MODULE') is None:
    import django
    print(os.environ.get('DJANGO_SETTINGS_MODULE'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remoteos.settings')
    print(os.environ.get('DJANGO_SETTINGS_MODULE'))
    django.setup()

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/10')


@app.task
def send_register_active_email(to_mail, username, token):
    # 发送激活邮件
    subject = "欢迎注册remoteos会员"
    from_mail = settings.EMAIL_FROM
    html_message = "<h1>%s, 欢迎光临</h1>点击链接激活账户<br/><a " \
                   "href='http://%s.%s/user/active/%s'>http://%s.%s/user/active/%s</a>" % (
                       username, DEVICE_UUID, PUBLIC_DOMAIN, token, DEVICE_UUID, PUBLIC_DOMAIN, token)
    send_mail(subject, '', from_mail, [to_mail], html_message=html_message)
    time.sleep(10)


@app.task
def real_playlist_request(url, index):
    # response_str = requests.get(url=url, headers=settings.SUYING_REQUEST_HEADER).content.decode()
    playlist_urls = cache.get("playlist_urls_result_cache")
    if playlist_urls is not None:
        return

    result = requests.get(url=settings.ONLINE_VIDEO_BASE_URL + url, headers=settings.ONLINE_VIDEO_REQUEST_HEADER).content.decode()
    result_html = etree.HTML(result)

    # 分集播放链接文件href
    js_href = result_html.xpath("/html/body/div[2]/div/div[1]/div/div/div/div[1]/script[1]/@src")

    result = requests.get(url=settings.ONLINE_VIDEO_BASE_URL + js_href[0], headers=settings.ONLINE_VIDEO_REQUEST_HEADER).content.decode()

    playlist_str = result[result.find('http'): -2]
    playlist_urls = re.findall('https.*?m3u8', playlist_str)
    playlist_urls = [unquote(item, 'utf-8') for item in playlist_urls]

    cache.set("playlist_urls_result_cache", {"playlist_urls": playlist_urls, "inx": index}, timeout=(3600 * 24))

    print("playlist urls result: \n", playlist_urls)

