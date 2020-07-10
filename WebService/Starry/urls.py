"""
Author: Baixu
Date: 2020-07-10
Desc:
    WebService的路由控制入口
"""

from django.conf.urls import url
from django.urls import path, include
from django.views.static import serve

from WebService.Starry import views as starry_views

urlpatterns = [
    url(r'(.*)$', starry_views.starry),
]