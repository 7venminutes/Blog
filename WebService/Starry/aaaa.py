"""
异步非阻塞调用demo，项目写好再删
"""
import time
from threading import Thread


def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


@async_call
def a():
    print('I\'m an a\n')
    time.sleep(10)
    print('I\'m an a after 3 seconds')


def b():
    print('I\'m a b')
    a()
    return 'b doesn\'t wait a'


print(b())
