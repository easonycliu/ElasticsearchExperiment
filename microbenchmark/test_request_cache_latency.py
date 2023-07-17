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

systick_1s = False
def systick_1s_generator(event):
    global systick_1s
    while not event.is_set():
        time.sleep(1)
        systick_1s = True
    print("Systick thread exiting")
    
query = {
    "size": 0,
    "aggs": {
        "range": {
            "date_range": {
                "field": "create_date",
                "format": "yyyy/MM/dd HH:mm:ss",
                "ranges": [
                    { "to": time.strftime("%Y/%m/%d %H:%M:%S", (2023, 1, 1, 0, 0, 0, 0, 0, 0)) },  
                    { "from": OPERATIONS["ADD_DATE_INFO"](None)["create_date"] } 
                ]
            }
        }
    }   
}

# query_file = open(os.path.join(os.getcwd(), "query", "nest_aggs.json"))
# query = json.load(query_file)
# query_file.close()
content = json.dumps(query) + "\n"

use_request_cache = "true" if len(sys.argv) == 1 else sys.argv[1]
url = "{}/_search?request_cache={}".format(HOST, use_request_cache)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
f = create_file("response", "w", curr_time)

event = threading.Event()
timer_thread = threading.Thread(target=systick_1s_generator, args=(event,))
timer_thread.start()

with httpx.Client(timeout=1.0) as client:
    latencies = []
    # for _ in range(2):
    while True:
        try:
            # time.sleep(0.01)
            if systick_1s:
                systick_1s = False
                start_time = time.time()
                response = client.post(url, content=content, headers={"Content-Type": "application/json"})
                latencies.append(time.time() - start_time)
                            
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            break
        except KeyError:
            print("A keyerror occured!")
            continue
        except httpx.ReadTimeout:
            print("Request timeout!")
            latencies.append(1.0)
            continue
    
    event.set()
    f.close()
    timer_thread.join()
    
    plt.plot([x for x in range(len(latencies))], latencies)
    plt.ylim((0, np.max(latencies) * 1.1))
    plt.xlabel("Time (s)")
    plt.ylabel("Latency (s)")
    
    fig_file = create_file("fig", "wb", curr_time, ".jpg")
    plt.savefig(fig_file)
    fig_file.close()
    
    throughput_in_sec_df = pd.DataFrame(latencies)
    data_file = create_file("data", "w", curr_time)
    throughput_in_sec_df.T.to_csv(data_file, ",")
    data_file.close()
