from django.shortcuts import render,redirect
import re
from user.models import User
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model,authenticate,login
from django.views.generic import View
from django.http import HttpResponse,HttpRequest,response
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #加密模块
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_email

User = get_user_model()
# Create your views here.
def register(request):
    '''显示注册页面'''
    if request.method == 'GET':
        return render(request,'register.html')
    else:
        '''进行注册处理'''
        # 1.接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 2.进行数据的校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 3.进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        # 4.返回应答,跳转至首页
        return redirect(reverse('goods:index'))

class RegisterView(View):
    '''注册'''
    def get(self,request):
        '''显示注册页面'''
        return render(request,'register.html')
    def post(self,request):
        '''进行注册处理'''
        # 1.接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 2.进行数据的校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 3.进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        #发送激活邮件，包含激活连接：http://127.0.0.1:8000/user/active/3
        #激活连接中需要包含用户的身份信息，并且要把身份信息进行加密处理
        #加密用户的身份信息，生成激活的token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        print(info)
        token = serializer.dumps(info)
        #字节流转为字符串类型
        token = token.decode()
        #发邮件
        subject = 'jiang的欢迎信息呀！'
        message = ''
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = '<h1>%s,欢迎您成为jiang的会员</h1>请点击以下链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)
        send_mail(subject,message,sender,receiver,html_message=html_message)
        # 4.返回应答,跳转至首页
        # send_register_active_email.delay(email,username,token)
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''用户激活'''
    def get(self,request,token):
        '''进行用户激活'''
        #进行用户解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']
            #根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            #跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            #激活链接已过期
            return HttpResponse('激活链接已过期')

class LoginView(View):
    '''登录'''
    def get(self,request):
        '''显示登录页面'''
        #判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        #使用模板
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        '''登录校验'''
        #接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        #校验数据
        if not all([username,password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        #业务处理：登录校验
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                #用户已激活时需要获取用户的登录状态
                login(request,user)
                print('用户已激活！')
                #判断是否需要记住用户名
                remember = request.POST.get('remember')
                #跳转到首页
                response = redirect(reverse('goods:index'))
                if remember == 'on':
                    #记住用户名
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                #返回response
                return response

            else:
                return render(request,'login.html',{'errmsg':'账户未激活'})
        else:
            #用户名密码错误
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})