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
from WebService.Starry.mediator import mediator

urlpatterns = [
    path('', starry_views.starry),
    url(r'submit_task/$', starry_views.receive_a_new_task),
    url(r'how_many_unfinished_tasks_now/$', starry_views.get_queue_length),
    url(r'give_me_my_task/$', starry_views.get_transformed_image_by_task_id),
    url(r'mediator/receive_finished_task/$', mediator.receive_finished_task_from_ServiceEnd),
    url(r'mediator/receive_failed_msg/$', mediator.receive_error_info_from_ServiceEnd),
    url(r'get_user_info/$', starry_views.get_user_info),
]
