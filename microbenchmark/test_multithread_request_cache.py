import json
import os
import signal
import random
import time
import threading
import httpx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append('')

from utils.file_operation import create_file
from operations.op_functions import OPERATIONS

port = 9200
HOST = "http://localhost:{}".format(port)

sender_number = 4

overall_throughput_in_sec = []
throughput = np.zeros(sender_number)
    
def throughput_collector(event):
    global overall_throughput_in_sec
    global throughput
    while not event.is_set():
        time.sleep(1)
        overall_throughput_in_sec.append(np.sum(throughput))
    print("Collector thread exiting")
    
def request_sender(event, id, url, query):
    global throughput
    start_time = (2010, 1, 1, 0, 0, 0, 0, 0, 0)
    start_time_stamp = time.mktime(start_time)
    end_time_stamp = time.time()
    
    client = httpx.Client(timeout=300000)
    random_times = [random.randint(int(start_time_stamp), int(end_time_stamp)) for _ in range(2)]

    while not event.is_set():
        random_time = random.choices(random_times, k=2)
        query["aggs"]["range"]["date_range"]["ranges"][0]["to"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(np.max(random_time)))
        query["aggs"]["range"]["date_range"]["ranges"][1]["from"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(np.min(random_time)))
        content = json.dumps(query) + "\n"
        response = client.post(url, content=content, headers={"Content-Type": "application/json"})
        throughput[id] += 1
    client.close()
    print("Sender {} thread exiting".format(id))
    
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
print("use request cache: {}".format(use_request_cache))
index = sys.argv[2] if len(sys.argv) > 2 else ""
print("index: {}".format(index))
url = "{}/{}/_search?request_cache={}".format(HOST, index, use_request_cache)

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
f = create_file("response", "w", curr_time)

event = threading.Event()
timer_thread = threading.Thread(target=throughput_collector, args=(event,))
timer_thread.start()

sender_threads = []
for i in range(sender_number):
    sender_threads.append(threading.Thread(target=request_sender, args=(event, i, url, query,)))
    sender_threads[-1].start()

# for _ in range(2):
while True:
    try:
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("Recieve keyboard interrupt from user, break")
        break
    except KeyError:
        print("A keyerror occured!")
        continue

event.set()
f.close()
timer_thread.join()
for sender_thread in sender_threads:
    sender_thread.join()

throughput_in_sec = [a - b for a, b in zip(overall_throughput_in_sec[:-1], [0] + overall_throughput_in_sec[:-2])]
plt.plot([x for x in range(len(throughput_in_sec))], throughput_in_sec)
plt.ylim((0, np.max(throughput_in_sec) * 1.1))
plt.xlabel("Time (s)")
plt.ylabel("Throughput (Number of Requests)")

print(np.mean(throughput_in_sec))

fig_file = create_file("fig", "wb", curr_time, ".jpg")
plt.savefig(fig_file)
fig_file.close()

throughput_in_sec_df = pd.DataFrame(throughput_in_sec)
data_file = create_file("data", "w", curr_time)
throughput_in_sec_df.T.to_csv(data_file, ",")
data_file.close()
