"""
depreciated.
该文件为利用django的ORM建立的数据模型，存储数据表file_tree的信息，
现相关信息的存储及交互代码已迁移至database/db_helpers/table_file_tree.py
[baixu] 2020-06-03
"""
from django.db import models


# Create your models here.
class FileTree(models.Model):
    """
    数据表FileTree
    """
    name = models.CharField(max_length=128)
    # dir = models.BigAutoField(unique=True)
    TYPE_CHOICE = ((u'D', u'dir'), (u'F', u'file'))
    type = models.CharField(max_length=4, choices=TYPE_CHOICE)
