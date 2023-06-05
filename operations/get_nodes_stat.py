import json
import os
import time
import httpx
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"
url = "{}/_nodes/stats".format(HOST)

response = httpx.get(url)

f = create_file("response", "w")
json.dump(response.json(), f, indent=2)
f.close()
