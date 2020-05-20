# 使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import time

app = Celery('celery_taaks.tasks', broker='reids://127.0.0.1:6379/8')

# 定义任务函数


@app.task
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    # 组织邮件信息
    subject = 'jiang的欢迎信息呀！'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [email]
    html_message = '<h1>%s,欢迎您成为jiang的会员</h1>请点击以下链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)
    send_mail(subject,message,sender,receiver,html_message=html_message)
    tiem.sleep(5)
