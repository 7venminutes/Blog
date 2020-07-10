"""
Author: Baixu
Date: 2020-07-10
Desc: 处理网站中starry风格迁移业务的视图请求
"""

from django.shortcuts import render


def starry(request, path):
    return render(request, 'Starry/starry.html')
