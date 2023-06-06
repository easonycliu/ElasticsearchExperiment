import asyncio
import httpx
import json

HOST = "http://127.0.0.1:9200"

async def main():
    q1 = {
        "index": ["test_{}".format(x) for x in range(5)],
        "expand_wildcards": "open",
        "ignore_unavailable": True,
        "allow_no_indices": True,
        "types": [],
        "search_type": "query_then_fetch",
        "ccs_minimize_roundtrips": True
    }
    q2 = {
        "from": 0,
        "size": 100,
        "timeout": "30s",
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

    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(10000, read=0.0001)) as client:
        await client.get(HOST, timeout=None)

        index = 0
        while True:
            try:
                index += 1
                response = await client.post(
                    "{}/_msearch?max_concurrent_searches=6&typed_keys=true".format(HOST), 
                    content=query_body, 
                    headers={"Content-Type": "application/json"}
                )
                print("{} {}".format(response, index))
            except httpx.ReadTimeout:
                pass

asyncio.run(main())
