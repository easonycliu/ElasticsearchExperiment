import asyncio
import json
import os
import time
import httpx
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"

async def post_request(client, url, request, init_time):
    response = await client.post(
        url,
        content=request,
        headers={"Content-Type": "application/json"}
    )
    success = True
    if "error" in response.json():
        success = False
        
    return {"time": time.time() - init_time,
            "success": success}

async def main():
    query = {
        "query": {
            "match": {
                "content": "life"
            }
        }
    }
    content = json.dumps(query) + "\n"
    url = "{}/_search?from=0&size=100".format(HOST)

    curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    task_list = []

    async with httpx.AsyncClient(timeout=30) as client:
        init_time = time.time()
        for _ in range(1000):
            task_list.append(asyncio.create_task(post_request(client, url, content, init_time)))
            
        log_data = await asyncio.gather(*task_list)
        log_data = sorted(log_data, key=lambda x: x["time"])
        
        time_used = []
        log_data_iter = iter(log_data)
        throughput = 0
        for start_time in range(int(np.floor(log_data[-1]["time"]))):
            throughput = 0
            while next(log_data_iter)["time"] < start_time + 1:
                throughput += 1
            time_used.append(throughput)
        plt.plot([x for x in range(len(time_used))], time_used)
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (Number of Requests)")
        plt.savefig(os.path.join(os.getcwd(), "fig", "fig_search_latency_{}.jpg".format(curr_time)))

asyncio.run(main())