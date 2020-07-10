#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
django项目的启动文件
命令行切换到该文件所在目录下：
python manage.py runserver 0.0.0.0:8000
可在8000端口启动该项目的服务
"""
import os
import sys
import django


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebService.settings')
    django.setup()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
