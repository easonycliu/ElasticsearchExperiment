import json
import os
import time
import httpx

HOST = "http://localhost:9200"
url = "{}/_nodes/stats".format(HOST)

response = httpx.get(url)

with open(os.path.join(os.getcwd(), "response", 
                        "response_{}".format(time.strftime('%Y%m%d%H%M%S', 
                                                            time.localtime(time.time())))), "w") as f:
    json.dump(response.json(), f, indent=2)
