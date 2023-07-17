import httpx
import json
import os
import time
import random
import sys
sys.path.append('')
sys.setrecursionlimit(3000)

from utils.file_operation import create_file

HOST = "http://localhost:9200"

def generate_deep_aggs(depth):
    q = {
        "size": 0,
        "aggs": {}
    }
    nest_aggs = q["aggs"]
    for i in range(depth):
        nest_aggs["histogram_by_char_num_{}".format(i)] = {
            "histogram": {
                "field": "content_char_num",
                "interval": random.randint(5, 1000),
                "min_doc_count": 0
            },
            "aggs": {}
        }
        nest_aggs = nest_aggs["histogram_by_char_num_{}".format(i)]["aggs"]
    
    nest_aggs["stats_char_num"] = {"stats": {"field": "content_char_num"}}
    
    file_name = "nest_aggs.json"
    f = open(os.path.join(os.getcwd(), "query", file_name), "w")
    json.dump(q, f, indent=4)
    f.close()
        
with httpx.Client() as client:
    # client.get(HOST, timeout=None)
    f = create_file("response", "w")
    q = generate_deep_aggs(50)
    # q["aggs"]["histogram_by_char_num"]["histogram"]["interval"] = random.randint(5, 20)
    # query_body = json.dumps(q) + "\n"
    # start_time = time.time()
    # response = client.post(
    #     f'{HOST}/_search', 
    #     content=query_body, 
    #     headers={"Content-Type": "application/json"}
    # )
        
    # f.write("use time : {}\nResponse : \n".format((time.time() - start_time) * 1000))
    # json.dump(response.json(), f, indent=4)
    # f.flush()
    f.close()
    