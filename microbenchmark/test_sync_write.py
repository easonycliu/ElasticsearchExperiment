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
from operations.create_rubbish_in_es import create_a_rubbish

port = 9200 if len(sys.argv) < 3 else sys.argv[2]
HOST = "http://localhost:{}".format(port)
index = "news"

data_buffer = Queue(maxsize=10)
def data_creator(event):
    global data_buffer
    while not event.is_set():
        data_buffer.put(create_a_rubbish())

    print("Creator thread exiting")
            
only_local = "" if len(sys.argv) < 3 else "&preference=_only_local"
url = "{}/_search?from=0&size=100{}".format(HOST, only_local)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) if len(sys.argv) == 1 else sys.argv[1]
curr_time = curr_time + str("" if len(sys.argv) < 3 else port)
f = create_file("response", "w", curr_time)

event = threading.Event()
creator = threading.Thread(target=data_creator, args=(event,))
creator.start()

with httpx.Client(timeout=300000) as client:
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
            data = data_buffer.get()
            response = client.post("{}/{}/_doc".format(HOST, index),
                               content=json.dumps(data) + "\n",
                               headers={"Content-Type": "application/json"})
            log_data.append({"time": int((time.time() - start_time) * 1000),
                             "start time": start_time - init_time})
            
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            end_time = time.time() - init_time
            break
        except KeyError:
            print("A keyerror occured!")
            continue
        except httpx.ReadTimeout:
            print("Read timeout")
            continue
    
    event.set()
    f.close()
    creator.join()
    
    throughput_in_sec = []
    log_data_iter = iter(log_data)
    throughput = 0
    for start_time in range(int(np.floor(end_time))):
        throughput = 0
        try:
            while next(log_data_iter)["start time"] < start_time + 1:
                throughput += 1
        except StopIteration:
            pass
        throughput_in_sec.append(throughput)
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
