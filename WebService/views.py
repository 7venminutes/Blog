"""
Author: Baixu
Date: 2020-07-10
Desc: 网站主入口的视图函数
"""
from django.shortcuts import render


def homepage(request):
    return render(request, 'homepage.html')
