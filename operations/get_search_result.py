import json
import os
import time
import httpx

client = httpx.Client()
file_name = 
# result = es.indices.create(index='news', ignore=400)
# print("create indices result : {}".format(result))

# data = {"title": "Save your life from boring works.", "url": "https://google.com"}
# result = es.create(index="news", id=2, document=data)
# print("create news result : {}".format(result))

query = {
    'match': {
        # 'title': 'life'
        'content': 'life'
    }
}

for x in range(5):
    result = es.search(index="test_{}".format(x), query=query)
    with open(os.path.join(os.getcwd(), "response", 
                        "response_{}".format(time.strftime('%Y%m%d%H%M%S', 
                                                            time.localtime(time.time())))), "w") as f:
        json.dump(dict(result), f, indent=2)
