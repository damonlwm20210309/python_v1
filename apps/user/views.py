from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
User = get_user_model()
import re
# Create your views here.
from django.views import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email

# /user/register
# def register(request):
#     '''注册'''
#     if request.method == 'GET':
#         return render(request, 'register.html')
#     else:
#         # 进行注册处理
#         # 接收数据
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#         # 校验数据
#         if not all([username, password, email]):
#             # 数据不完整
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#
#         # 校验邮箱
#         if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '请勾选协议！'})
#
#         # 校验用户名是否存在
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             # 用户名不存在
#             user = None
#
#         if user:
#             # 用户名已存在
#             return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#         # 进行业务处理：进行用户注册
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0
#         user.save()
#
#         # 返回应答，跳转到首页
#         return redirect(reverse('goods:index'))
#
#
#
# def register_handle(request):
#     '''注册页面处理'''
#     # 接收数据
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#     # 校验数据
#     if not all([username, password, email]):
#         # 数据不完整
#         return render(request, 'register.html', {'errmsg':'数据不完整'})
#
#     # 校验邮箱
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, 'register.html', {'errmsg':'邮箱格式不正确'})
#
#     if allow != 'on':
#         return render(request, 'register.html', {'errmsg':'请勾选协议！'})
#
#     # 校验用户名是否存在
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#
#     if user:
#         # 用户名已存在
#         return render(request, 'register.html', {'errmsg':'用户名已存在'})
#
#     # 进行业务处理：进行用户注册
#     user = User.objects.create_user(username, email, password)
#     user.is_active = 0
#     user.save()
#
#     # 返回应答，跳转到首页
#     return redirect(reverse('goods:index'))

class RegisterView(View):
    '''注册'''
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 进行注册处理
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 校验数据
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选协议！'})

        # 校验用户名是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 加密用户的信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发邮件
        send_register_active_email.delay(email, username, token)

        # 返回应答，跳转到首页
        return redirect(reverse('goods:index'))

class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        print('用户激活的get方法')
        # 用户解密
        serializer = Serializer(settings.SECRET_KEY, 5)
        try:
            info = serializer.loads(token)
            # 获取待激活的用户id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active=1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')


class LoginView(View):
    '''登录'''
    def get(self, request):
        '''显示登录页面'''
        return render(request, 'login.html')




