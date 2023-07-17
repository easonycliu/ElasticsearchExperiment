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
    
def request_sender(event, id, url, content):
    global throughput
    client = httpx.Client(timeout=300000)
    while not event.is_set():
        response = client.post(url, content=content, headers={"Content-Type": "application/json"})
        throughput[id] += 1
    client.close()
    print("Sender {} thread exiting".format(id))
    
query = {
    "size": 0,
    "aggs": {
        "contents": {
            "terms": { "field": "content" }
        }
    }
}

url = "{}/_search".format(HOST)
content = json.dumps(query) + "\n"

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
f = create_file("response", "w", curr_time)

event = threading.Event()
timer_thread = threading.Thread(target=throughput_collector, args=(event,))
timer_thread.start()

sender_threads = []
for i in range(sender_number):
    sender_threads.append(threading.Thread(target=request_sender, args=(event, i, url, content,)))
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

fig_file = create_file("fig", "wb", curr_time, ".jpg")
plt.savefig(fig_file)
fig_file.close()

throughput_in_sec_df = pd.DataFrame(throughput_in_sec)
data_file = create_file("data", "w", curr_time)
throughput_in_sec_df.T.to_csv(data_file, ",")
data_file.close()
