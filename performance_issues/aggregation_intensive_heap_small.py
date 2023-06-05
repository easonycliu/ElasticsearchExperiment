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
            "dropoff_datetime": {
                "gte": "A",
                "lt": "G"
            }
        }
        # "match": {
        #     "content": "life"
        # }
    },
    "aggs": {
        "dropoffs_over_time": {
            "date_histogram": {
                "field": "dropoff_datetime",
                "calendar_interval": "week",
                "time_zone": "America/New_York"
            }
        }
    }
}

query_body = json.dumps(q) + "\n"

with httpx.Client() as client:
    client.get(HOST, timeout=None)
    response = client.post(
        f'{HOST}/_search?from=0&size=10000', 
        content=query_body, 
        headers={"Content-Type": "application/json"}
    )
    
    f = create_file("response", "a")
    json.dump(response.json(), f, indent=2)
    f.close()
    