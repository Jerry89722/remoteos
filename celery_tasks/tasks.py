"""
import socket
import os

from celery import Celery


def socket_init():
    # logging.warning("socket init----")
    try:
        ss = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ss.connect("/home/zjay/vlc.sock")
        print("socket init ok")
        return ss
    except socket.error as msg:
        print("unix socket create failed", msg)

    return None


sock = None
if os.environ.get('DJANGO_SETTINGS_MODULE') is None:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remoteos.settings')
    django.setup()
    sock = socket_init()


app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/6')


@app.task
def vlc_request(act, file_path):
    # play /xxx/xxx.mp4
    result = None
    if act == 'play':
        print("[tasks] file_path: ", file_path)
        cmd = "add " + file_path + "\r\n"
        print("----------------- cmd start: ", cmd)
        print("----------------- cmd end: ", cmd)
        result = play_request(cmd)
        print("request result: ", result)


def play_request(cmd):
    global sock
    try:
        sock.sendall(cmd.encode())
    except IOError as msg:
        print(msg)
    else:
        print("unknown error occurred when sendall")
    resp_str = sock.recv(1024).decode()
    print("---------------------------vlc response: ")
    print(resp_str)
    print("---------------------------vlc response end")
    return resp_str
"""

from celery import Celery
from remoteos import settings
from django.core.mail import send_mail
import os

from remoteos.settings import DEVICE_UUID, PUBLIC_DOMAIN

if os.environ.get('DJANGO_SETTINGS_MODULE') is None:
    import django
    print(os.environ.get('DJANGO_SETTINGS_MODULE'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'remoteos.settings')
    print(os.environ.get('DJANGO_SETTINGS_MODULE'))
    django.setup()

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')


@app.task
def send_register_active_email(to_mail, username, token):
    # 发送激活邮件
    subject = "欢迎注册remoteos会员"
    from_mail = settings.EMAIL_FROM
    html_message = "<h1>%s, 欢迎光临</h1>点击链接激活账户<br/><a " \
                   "href='http://%s.%s/user/active/%s'>http://%s.%s/user/active/%s</a>" % (
                       username, DEVICE_UUID, PUBLIC_DOMAIN, token, DEVICE_UUID, PUBLIC_DOMAIN, token)
    send_mail(subject, '', from_mail, [to_mail], html_message=html_message)
