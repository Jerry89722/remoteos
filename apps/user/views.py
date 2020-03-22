import json

from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.views.generic.base import View
from itsdangerous import TimedJSONWebSignatureSerializer as TJSS, SignatureExpired
from user.models import User
from celery_tasks import tasks
from remoteos import settings


class RegisterView(View):

    def post(self, request):
        """进行注册处理"""
        print("register post handle")
        # 接收数据
        username = request.POST.get('username')
        print("username: ", username)
        password = request.POST.get('pwd')
        print("password: ", password)
        cpassword = request.POST.get('cpwd')
        print("cpassword: ", cpassword)
        phone = request.POST.get('phone')
        print("phone: ", phone)
        email = request.POST.get('email')
        print("email: ", email)
        allow = request.POST.get('allow')
        print("allow: ", allow)

        # 数据校验
        if not all([username, password, cpassword, email, phone, allow]):
            # 数据不完整
            return HttpResponse("用户数据不完整")
        # 校验邮箱
        # if not re.match():
        #     return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return HttpResponse("请同意注册协议")

        # 进行业务处理
        try:
            user = User.objects.get(username=username)
            user_admin = User.objects.get(is_admin=True)
        except User.DoesNotExist:
            user = None
            user_admin = None

        if user is None:
            user = User.objects.create_user(username, email, password)
            user.phone = phone
            user.is_active = 0
            if user_admin is None:
                user.is_admin = True
            user.save()

            ss = TJSS(settings.SECRET_KEY, 3600)
            info = {"id": user.id}
            token = ss.dumps(info).decode()
            tasks.send_register_active_email.delay(email, username, token)
        else:
            print("用户已存在, 注册失败")
            if user.is_active == 0:
                return HttpResponse('用户名已存在, 但未激活')
            else:
                return HttpResponse('用户名已存在, 注册失败')

        # 返回结果应答
        return HttpResponse("等待激活")


class ActiveView(View):
    def get(self, request, token):
        ss = TJSS(settings.SECRET_KEY, 3600)  # 3600s
        try:
            res = ss.loads(token)
            user = User.objects.get(id=res['id'])
            user.is_active = 1
            user.save()
            return HttpResponse("ok")
        except SignatureExpired:
            return HttpResponse("激活超时")


class LoginView(View):
    def get(self, request):
        # 记住用户名
        account = ''
        checked = ''
        if 'account' in request.COOKIES:
            account = request.COOKIES.get('account')
            print("account: ", account)
            checked = 'checked'
        response_dict = {'account': account, 'checked': checked}
        return HttpResponse(json.dumps(response_dict))

    def post(self, request):
        account = request.POST.get('account')
        pwd = request.POST.get('pwd')
        remember = request.POST.get('remember')
        if not all([account, pwd]):
            return HttpResponse('用户名密码不能为空')
        if account.isdigit():
            username = User.objects.get(phone=account)
        else:
            username = account
        user = authenticate(username=username, password=pwd)
        if user is None:
            return HttpResponse('账户无效')
        else:
            response = HttpResponse("ok")
            login(request, user)
            if remember == 'on':
                response.set_cookie('account', account, max_age=3600*24*7)
                response.set_cookie('password', pwd, max_age=3600*24*7)
            else:
                response.delete_cookie('account')
                response.delete_cookie('password')
                response.delete_cookie('remember')

            return response


class UserInfoView(View):

    def get(self, request):
        userinfo_dict = {'username': "xxx", "phone": "15818632692"}
        return HttpResponse(json.dumps(userinfo_dict))

