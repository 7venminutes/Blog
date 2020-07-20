from __future__ import print_function

import requests

from WebService.Starry.proto.task_common_pb2 import StarryPost

request = StarryPost()
request.taskId = "1234"
request.modelSelect = 2
request.image.type = 2
# 2950526-75ec174d6714c185.png
# 2950526-66c8f2dd342ac6d6.jpg
with open(r"C:\Users\ThinkPad\Pictures\2950526-75ec174d6714c185.png", 'rb') as img:
    f = img.read()
    request.image.image = f


s = requests
r = s.post("http://127.0.0.1:5000/transfer", request.SerializeToString())

print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)
print(r.text)
