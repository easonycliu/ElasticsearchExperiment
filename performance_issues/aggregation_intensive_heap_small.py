import httpx
import json
import os
import time
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"

q = {
    "size": 0,
    "query": {
        "range": {
            "title": {
                "gte": "a",
                "lt": "b"
            }
        }
    },
    "aggs": {
        "histogram_by_char_num": {
            "histogram": {
                "field": "content_char_num",
                "interval": 10,
                "min_doc_count": 0
            },
            "aggs": {
                "histogram_by_char_num_small": {
                    "histogram": {
                        "field": "content_char_num",
                        "interval": 5,
                        "min_doc_count": 0
                    },
                    "aggs": {
                        "stats_char_num": {
                            "stats": {
                                "field": "content_char_num",
                            }
                        }
                    }
                }
            }
        }
    }
}

query_body = json.dumps(q) + "\n"

with httpx.Client() as client:
    client.get(HOST, timeout=None)
    f = create_file("response", "w")
    start_time = time.time()
    response = client.post(
        f'{HOST}/_search?from=0&size=10000', 
        content=query_body, 
        headers={"Content-Type": "application/json"}
    )
        
    f.write("{}. {}, use time : {}\n".format(0, response, (time.time() - start_time) * 1000))
    f.flush()
    f.close()
    
    
    