# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-07-13
Desc: 文件资源的展示（与文件下载的大体逻辑相同，权限判断时查看的权限字段不同，返回的content-type不同
"""
import os

from django.http import HttpResponse, Http404

from common import address_transfer
from database.db_helpers import table_access, db_helper
from WebService.FilesCube.views.tools.download.views import get_file_response


def display_static_file(request, file_path):
    """
    处理展示静态文件的视图请求
    """
    try:
        username = request.session['username']
    except KeyError:
        username = 'anonymous_user'

    # 对path合法性判断一下
    file_path = str(file_path)

    _, file_path = address_transfer.change_path_to_common_path(file_path)

    access_list = table_access.get_access_list_by_id(username)
    if not db_helper.lookup_access_in_the_list(file_path, 'read', access_list):
        return HttpResponse('no read access to resource', status=403)
    elif not db_helper.lookup_access_in_the_list(file_path, 'download', access_list):
        return HttpResponse('no download access to resource', status=403)
    else:
        transfer_state, actual_path = address_transfer.resolve_path_to_actual_path(file_path)
        if transfer_state and not os.path.exists(actual_path):
            raise Http404('"%(path)s" does not exist' % {'path': file_path})
        elif not transfer_state:
            raise Http404('"%(path)s" can not be resolved properly' % {'path': file_path})
        elif os.path.isdir(actual_path):
            # fixme[baixu] 此处应该展示文件夹内的所有目录项，而不是返回403
            return HttpResponse('server does not support downloading a folder', status=403)
        else:
            # 一切均正常，返回文件
            return get_file_response(request, actual_path, 'display')
