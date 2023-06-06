import asyncio
import httpx
import json
import os
import time
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"

async def post_request(client, url, request, index):
    response = await client.post(
        url,
        content=request,
        headers={"Content-Type": "application/json"}
    )
    return {"index": index, "response": response.json()}

async def main():
    q1 = {
        "index": ["test_{}".format(x) for x in range(5)],
        "expand_wildcards": "open",
        "ignore_unavailable": True,
        "allow_no_indices": True,
        "search_type": "query_then_fetch",
        "ccs_minimize_roundtrips": True
    }
    q2 = {
        "from": 0,
        "size": 1000,
        "timeout": "60s",
        "query": {
            "bool": {
                "filter": [{
                    "terms": {
                        "content": ["life"],
                        "boost": 1.0
                    }
                }],
                "adjust_pure_negative": True,
                "boost": 1.0
            }
        }
    }
    query_body = json.dumps(q1) + "\n" + json.dumps(q2) + "\n"
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(1)) as client:
        await client.get(HOST, timeout=None)
        
        task_list = []
        url = "{}/_msearch?max_concurrent_searches=6&typed_keys=true".format(HOST)
        
        index = 0
        timeout_times = 0
        while True:
            try:
                for _ in range(1000):
                    index += 1
                    task_list.append(asyncio.create_task(post_request(client, url, query_body, index)))
                
                query_result = await asyncio.gather(*task_list)
                task_list.clear()
                f = create_file("response", "a")
                for one_result in query_result:
                    f.write("index {} get search result {}\n".format(one_result["index"], one_result["response"]["responses"][0]["hits"]["hits"][0]["_source"]["title"]))
                f.close()
            except httpx.ReadTimeout:
                timeout_times += 1
                task_list.clear()
                print("recieve time out exception {} times, restart".format(timeout_times))
                pass
                    
asyncio.run(main())
