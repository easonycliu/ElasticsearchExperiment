import asyncio
import httpx
import json
import os
import time
from random_words import RandomWords
import sys
sys.path.append('')

from utils.file_operation import create_file

def get_all_search_result(client, host):
    
    scroll_search_query = {
        "doc": {},
        "stored_fields": [],
        "size": 1000
    }
    response = client.post(
        "{}/_update?scroll=1m".format(host),
        content=json.dumps(scroll_search_query) + "\n",
        headers={"Content-Type": "application/json"}
    )
    
    response_json = response.json()
    while (len(response_json["hits"]["hits"]) > 0):
        print("Complete One Search")
        scroll_id = response_json["_scroll_id"]
        scroll_query = {
            "scroll": "1m",
            "scroll_id": scroll_id
        }
        response = client.post(
            "{}/_search/scroll".format(host),
            content=json.dumps(scroll_query) + "\n",
            headers={"Content-Type": "application/json"}
        )
        response_json = response.json()
        
        