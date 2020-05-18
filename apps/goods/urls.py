
from django.contrib import admin
from django.urls import re_path,include
from goods import views
urlpatterns = [
    re_path(r'^index$',views.index,name='index'),#首页
    re_path(r'^$',views.index,name='idnex'),#为空时仍然显示首页
]
