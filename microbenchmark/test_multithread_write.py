import json
import os
import signal
import time
import threading
from queue import Queue
import httpx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append('')

from utils.file_operation import create_file
from operations.create_rubbish_in_es import fast_create_a_rubbish

port = 9200 if len(sys.argv) < 3 else sys.argv[2]
HOST = "http://localhost:{}".format(port)
index = "test2"

creator_number = 2
sender_number = 2

start = False

def signal_handler(signalnum, frame):
    global start
    print("Recieve {} at frame {}".format(signalnum, frame))
    start = True
signal.signal(signal.SIGUSR1, signal_handler)

data_buffer = Queue(maxsize=2000)

def data_creator(event):
    global data_buffer
    while not event.is_set():
        if data_buffer.full():
            print("Buffer full")
        data_buffer.put(fast_create_a_rubbish())

    print("Creator thread exiting")

overall_throughput_in_sec = []
throughput = np.zeros(sender_number)

def throughput_collector(event):
    global overall_throughput_in_sec
    global throughput
    while not event.is_set():
        time.sleep(1)
        overall_throughput_in_sec.append(np.sum(throughput))
    print("Collector thread exiting")

def request_sender(event, id, url):
    global throughput
    print("Create request sender {}".format(id))
    client = httpx.Client(timeout=300000)
    while not event.is_set():
        query = data_buffer.get()
        print("Sender {} sending a new update request, current buffer size is {}".format(id, data_buffer.qsize()))
        content = json.dumps(query) + "\n"
        response = client.post(url, content=content, headers={"Content-Type": "application/json"})
        response_json = response.json()
        if "error" in response_json.keys():
            print("An error occored in sender {}, {}!".format(id, response_json["error"]))
        throughput[id] += 1
    client.close()
    print("Sender {} thread exiting".format(id))
            
url = "{}/{}/_doc?refresh=false".format(HOST, index)

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) if len(sys.argv) == 1 else sys.argv[1]
curr_time += "write"

event = threading.Event()

creator_threads = []
for i in range(creator_number):
    creator_threads.append(threading.Thread(target=data_creator, args=(event,)))
    creator_threads[-1].start()

while not start:
    time.sleep(0.1)

timer_thread = threading.Thread(target=throughput_collector, args=(event,))
timer_thread.start()

sender_threads = []
for i in range(sender_number):
    sender_threads.append(threading.Thread(target=request_sender, args=(event, i, url,)))
    sender_threads[-1].start()
    
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("Recieve keyboard interrupt from user, break")
        break
    
event.set()
for index in range(len(sender_threads)):
    sender_threads[index].join()
for index in range(len(creator_threads)):
    creator_threads[index].join()
timer_thread.join()

throughput_in_sec = [a - b for a, b in zip(overall_throughput_in_sec[:-1], [0] + overall_throughput_in_sec[:-2])]

plt.plot([x for x in range(len(throughput_in_sec))], throughput_in_sec)
plt.xlabel("Time (s)")
plt.ylabel("Throughput (Number of Requests)")

fig_file = create_file("fig", "wb", curr_time, ".jpg")
plt.savefig(fig_file)
fig_file.close()

throughput_in_sec_df = pd.DataFrame(throughput_in_sec)
f = create_file("data", "w", curr_time)
throughput_in_sec_df.T.to_csv(f, ",")
f.close()
