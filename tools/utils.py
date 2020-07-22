import os
import shutil


def make_dir_if_not_exists(dir_name, delete_first=False):
    if delete_first and os.path.exists(dir_name):
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)
        else:
            os.remove(dir_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
