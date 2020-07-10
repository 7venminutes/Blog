"""
Author: Baixu
Date: 2020-07-10
Desc:
    WebService的路由控制入口
"""

from django.conf.urls import url
from django.urls import path, include
from django.views.static import serve

from WebService import views as webservice_views

urlpatterns = [
    url(r'^$', webservice_views.homepage),
    path('blog/', include('WebService.Blog.urls')),
    path('filescube/', include('WebService.FilesCube.urls')),
    path('starry/', include('WebService.Starry.urls')),
    # url(r'^(?P<path>.*)$', serve, {'document_root': 'FilesCube/static/easyui'}),
]
