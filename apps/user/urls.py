
from django.contrib import admin
from django.urls import re_path,include
from user import views
from user.views import RegisterView
urlpatterns = [
    # re_path(r'^register$',views.register,name='register'),
    # re_path(r'^register_handle$',views.register_handle,name='register_handle'),#注册处理
    re_path(r'^register$', RegisterView.as_view(), name='register'),  # 注册
]
