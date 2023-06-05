import json
import os
import time
import httpx
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
url = "{}/_search?from=0&size=10000".format(HOST)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
f = create_file("response", "w")

with httpx.Client(timeout=10) as client:
    while True:
        try:
            time.sleep(1)
            start_time = time.time()
            response = client.post(url, content=content, headers={"Content-Type": "application/json"})
            response_json = response.json()
            log_data.append({"time": int((time.time() - start_time) * 1000),
                             "result": response_json["hits"]["hits"][0]["_source"]["title"]})
            f.write("time used : {}, result : {}\n".format(log_data[-1]["time"], log_data[-1]["result"]))
            f.flush()
            
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            break
    
    f.close()
    
    time_used = []
    for data in log_data:
        time_used.append(data["time"])
    plt.plot([x for x in range(len(time_used))], time_used)
    plt.ylabel("Latency (ms)")
    plt.savefig(os.path.join(os.getcwd(), "fig", "fig_search_latency_{}.jpg".format(curr_time)))
