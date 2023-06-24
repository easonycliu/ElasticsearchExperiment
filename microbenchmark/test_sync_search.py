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

query = {
    "query": {
        "match": {
            "content": "life"
        }
    }
}
content = json.dumps(query) + "\n"
url = "{}/news/_search?from=0&size=100".format(HOST)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
f = create_file("response", "w")

with httpx.Client(timeout=300) as client:
    init_time = None
    end_time = 0
    while True:
        try:
            # time.sleep(0.01)
            if init_time is None:
                init_time = time.time()
                start_time = init_time
            else:
                start_time = time.time()
            response = client.post(url, content=content, headers={"Content-Type": "application/json"})
            response_json = response.json()
            log_data.append({"time": int((time.time() - start_time) * 1000),
                             "start time": start_time - init_time,
                             "result": response_json["hits"]["hits"][0]["_source"]["title"]})
            f.write("time used : {}, start time : {}, result : {}\n".format(log_data[-1]["time"], log_data[-1]["start time"], log_data[-1]["result"]))
            f.flush()
            
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            end_time = time.time() - init_time
            break
    
    f.close()
    
    time_used = []
    log_data_iter = iter(log_data)
    throughput = 0
    for start_time in range(int(np.floor(end_time))):
        throughput = 0
        try:
            while next(log_data_iter)["start time"] < start_time + 1:
                throughput += 1
        except StopIteration:
            pass
        time_used.append(throughput)
    plt.plot([x for x in range(len(time_used))], time_used)
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Number of Requests)")
    plt.savefig(os.path.join(os.getcwd(), "fig", "fig_search_latency_{}.jpg".format(curr_time)))
