"""hfs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from django.views.static import serve

from WebService.FilesCube import FilesCube_views as FilesCube_views
from WebService.FilesCube.views.tools import views as tools_views, display_rss
from WebService.FilesCube.views.index import views as index

urlpatterns = [
    url(r'^$', FilesCube_views.index),
    url(r'^logout/', FilesCube_views.logout, name='logout'),
    url(r'/~.~//', index.homepage),
    url('admin/', admin.site.urls),
    url(r'authentication/$', FilesCube_views.authentication),
    path('index/', include('WebService.FilesCube.views.index.urls')),
    path('access_management/', include('WebService.FilesCube.views.access_management.urls')),
    path('user_management/', include('WebService.FilesCube.views.user_management.urls')),
    path('volume_management/', include('WebService.FilesCube.views.volume_management.urls')),
    path('tools/', include('WebService.FilesCube.views.tools.urls')),
    url(r'^qrcode/(.+)$', tools_views.generate_qr_code, name='qrcode'),
    url(r'(.+)$', display_rss.display_static_file),
]
