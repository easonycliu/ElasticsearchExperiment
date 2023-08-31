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
        
# query = {
#     "size": 0,
#     "aggs": {
#         "range": {
#             "date_range": {
#                 "field": "create_date",
#                 "format": "yyyy/MM/dd HH:mm:ss",
#                 "ranges": [
#                     {"to": time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))},
#                     {"from": OPERATIONS["ADD_DATE_INFO"](None)["create_date"]}
#                 ]
#             }
#         }
#     }
# }

start_time = (2010, 1, 1, 0, 0, 0, 0, 0, 0)
end_time = (2023, 1, 1, 0, 0, 0, 0, 0, 0)
start_time_stamp = time.mktime(start_time)
start_time_list = np.zeros(10000)
for i in range(10000):
    start_time_list[i] = start_time_stamp
    start_time_stamp += 1
    
query = {
    "size": 0,
    "query": {
        "range": {
            "create_date": {
                "gte": time.strftime("%Y/%m/%d %H:%M:%S", start_time),
                "lt": time.strftime("%Y/%m/%d %H:%M:%S", end_time)
            }
        }
    },
    "aggs": {
        "sales_over_time": {
            "date_histogram": {
                "field": "create_date",
                "calendar_interval": "minute",
                "min_doc_count": 0
            }
        }
    }
}

# query_file = open(os.path.join(os.getcwd(), "query", "nest_aggs.json"))
# query = json.load(query_file)
# query_file.close()

use_request_cache = "true" if len(sys.argv) == 1 else sys.argv[1]
url = "{}/_search?request_cache={}".format(HOST, use_request_cache)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
f = create_file("response", "w", curr_time)

event = threading.Event()
timer_thread = threading.Thread(target=systick_1s_generator, args=(event,))
timer_thread.start()

with httpx.Client(timeout=300000) as client:
    init_time = time.time()
    throughput_in_sec = []
    throughput = 0
    start_time_index = 0
    # for _ in range(2):
    while True:
        try:
            # time.sleep(0.01)
            if systick_1s:
                systick_1s = False
                throughput_in_sec.append(throughput)
                throughput = 0
            # query["query"]["range"]["create_date"]["gte"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(random.choice(start_time_list)))
            start_time_index += 1
            content = json.dumps(query) + "\n"
            start_time = time.time()
            response = client.post(url, content=content, headers={"Content-Type": "application/json"})
            throughput += 1
            # response_json = response.json()
            # print(response_json)
            # log_data.append({"time": int((time.time() - start_time) * 1000),
            #                  "start time": start_time - init_time,
            #                  "result": response_json["aggregations"]})
            # f.write("time used : {}, start time : {}, result : {}\n".format(log_data[-1]["time"], log_data[-1]["start time"], log_data[-1]["result"]))
            # f.flush()
            
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            break
        except KeyError:
            print("A keyerror occured!")
            print("Response is : {}".format(response_json))
            continue
    
    event.set()
    f.close()
    timer_thread.join()
    
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
