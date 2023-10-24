import asyncio
import httpx
import json
import os
import time
from random_words import RandomWords
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"

def generate_awkward_query(operation_num):
    q = {
        "timeout": "60s",
        "from": 0,
        "size": 10000,
        "query": {
            "bool": {
                "should": [],
                "minimum_should_match": 1
            }
        }
    }
    
    word_creator = RandomWords()
    for _ in range(operation_num):
        word = word_creator.random_word()
        item = {
          "match": {
            "content": word
          }
        }
        q["query"]["bool"]["should"].append(item)
        
    file_name = "boolean_search_interfere.json"
    f = open(os.path.join(os.getcwd(), "query", file_name), "w")
    json.dump(q, f, indent=4)
    f.close()

def get_all_search_result(client, host):
    
    f = open(os.path.join(os.getcwd(), "query", "boolean_search.json"))
    search_query = json.load(f)
    f.close()
    scroll_search_query = {
        "query": search_query["query"],
        "stored_fields": [],
        "size": 1000
    }
    response = client.post(
        "{}/_search?scroll=1m".format(host),
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
    
# with httpx.Client(timeout=None) as client:
#     get_all_search_result(client, HOST)
generate_awkward_query(800)
