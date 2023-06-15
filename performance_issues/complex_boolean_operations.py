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

def generate_awkward_query():
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
    for _ in range(8000):
        word = word_creator.random_word()
        item = {
          "match": {
            "content": word
          }
        }
        q["query"]["bool"]["should"].append(item)
        
    file_name = "boolean_search.json"
    f = open(os.path.join(os.getcwd(), "query", file_name), "w")
    json.dump(q, f, indent=4)
    f.close()

async def post_request(client, url, request, index):
    response = await client.post(
        url,
        content=request,
        headers={"Content-Type": "application/json"}
    )
    return {"index": index, "response": response.json()}

async def main():
    q = {
        "timeout": "60s",
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "content": "life"
                    }
                },
                "should": [
                    {
                        "match": {
                            "content": "door"
                        }
                    },
                    {
                        "match": {
                            "content": "apple"
                        }
                    },
                    {
                        "match": {
                            "content": "bull"
                        }
                    },
                    {
                        "match": {
                            "content": "reason"
                        }
                    },
                    {
                        "match": {
                            "content": "road"
                        }
                    },
                    {
                        "match": {
                            "content": "shop"
                        }
                    },
                    {
                        "match": {
                            "content": "man"
                        }
                    }
                ],
                "minimum_should_match": 1,
                "must_not": [
                    {
                        "match": {
                            "title": "Breaking"
                        }
                    }
                ],
                # "filter": [{
                #     "terms": {
                #         "content": ["life"],
                #         "boost": 1.0
                #     }
                # }],
                # "adjust_pure_negative": True,
                # "boost": 1.0
            }
        }
    }
    query_body = json.dumps(q) + "\n"
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(100)) as client:
        await client.get(HOST, timeout=None)
        
        url = "{}/news/_search?from=0&size=10000".format(HOST)
        
        index = 0
        timeout_times = 0
        while True:
            try:
                query_result = []
                for _ in range(1):
                    index += 1
                    response_data = await post_request(client, url, query_body, index)
                    query_result.append(response_data)
                
                # f = create_file("response", "a")
                for one_result in query_result:
                    if "error" in one_result["response"].keys():
                        print(one_result["response"])
                        break
                    # f.write("index {} get search result {}\n".format(one_result["index"], one_result["response"]["hits"]["hits"]))
                # f.close()
                return
            except httpx.ReadTimeout:
                timeout_times += 1
                print("recieve time out exception {} times, restart".format(timeout_times))
                pass
                    
# asyncio.run(main())
generate_awkward_query()
