import os
import signal
import time
import random
import threading
import itertools
import httpx
import matplotlib.pyplot as plt
import numpy as np
import json
import sys
sys.path.append('')

from utils.file_operation import create_file
from operations.op_functions import OPERATIONS

port = 9200
HOST = "http://localhost:{}".format(port)

file_name = sys.argv[3]

log_for_parties = None
if len(sys.argv) > 5:
    log_for_parties = sys.argv[5]

throughput = 0
def signal_handler(signalnum, frame):
    global throughput
    output_file = open(file_name, 'a')
    output_file.write(str(throughput) + "\n")
    output_file.close()
    throughput = 0
    
signal.signal(signal.SIGUSR1, signal_handler)
    
query = {
    "size": 0,
    "aggs": {
        "range": {
            "date_range": {
                "field": "create_date",
                "format": "yyyy/MM/dd HH:mm:ss",
                "ranges": [
                    { "to": "" },  
                    { "from": "" } 
                ]
            }
        }
    }   
}

use_request_cache = sys.argv[1] if len(sys.argv) > 1 else "true"
index = sys.argv[2] if len(sys.argv) > 2 else ""
url = "{}/{}/_search?request_cache={}".format(HOST, index, use_request_cache)

print("use request cache: {}".format(use_request_cache))
print("index: {}".format(index))

start_time = (2010, 1, 1, 0, 0, 0, 0, 0, 0)
start_time_stamp = time.mktime(start_time)
end_time_stamp = time.time()

client = httpx.Client(timeout=300000)
random_times = [random.randint(int(start_time_stamp), int(end_time_stamp)) for _ in range(8)]
time_combinations = list(itertools.combinations(random_times, 2))
# print(random_times)

i = 0
latency_list = []
while True:
    try:
        random_time = time_combinations[i]
        i = (i + 1) % len(time_combinations)
        query["aggs"]["range"]["date_range"]["ranges"][0]["to"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(np.max(random_time)))
        query["aggs"]["range"]["date_range"]["ranges"][1]["from"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(np.min(random_time)))
        content = json.dumps(query) + "\n"
        start = time.time_ns()
        start_us = int(start / 1000)
        response = client.post(url, content=content, headers={"Content-Type": "application/json"})
        end = time.time_ns()
        end_us = int(end / 1000)
        latency_list.append(end - start)
        if log_for_parties is not None:
            with open(log_for_parties, "a") as f:
                f.write("{}\n".format(end_us - start_us))
        response_json = response.json()
        if "error" in response_json.keys():
            print("An error occored in sender {}, {}!".format(id, response_json["error"]))
            continue
        throughput += 1
    except KeyboardInterrupt:
        latency_file = open(sys.argv[4], "w")
        for latency in latency_list[1:]:
            latency_file.write(str(latency) + "\n")
        latency_file.close()
        break
    except KeyError:
        continue

client.close()
