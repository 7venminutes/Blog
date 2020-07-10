# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/09
Desc: tools模块的路由控制文件，根据不同的路径判断由哪个视图函数来处理请求
"""
from django.conf.urls import url
from WebService.FilesCube.views.tools import views as tools
from WebService.FilesCube.views.tools.upload import views as upload
from WebService.FilesCube.views.tools.download import views as download

urlpatterns = [
    url(r'qr-code/?$', tools.generate_qr_code),
    url(r'txt-preview/?$', tools.preview_file_content),
    url(r'save-txt/?$', tools.save_txt_file),
    url(r'upload_page/?$', upload.uploadPage),
    url(r'upload_part/?$', upload.upload),
    url(r'upload_success/?$', upload.upload_success),
    url(r'upload/check/?$', upload.check_access),
    url(r'upload/check_chunk/?$', upload.check_chunk),
    url(r'download/(.+)$', download.download),
    url(r'download/(.+)$', download.get_file_response, {'document_root': 'E:\\zhfs\\'}),
    url(r'^download/(files/.*)$', download.get_file_response, {'document_root': 'E:\\zhfs\\'})
]
