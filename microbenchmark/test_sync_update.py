import json
import os
import signal
import time
import httpx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append('')

from utils.file_operation import create_file

assert len(sys.argv) == 3, "Usage: test_sync_update.py [index] [doc_id]"

index = sys.argv[1]
doc_id = sys.argv[2]
port = 9200
HOST = "http://localhost:{}".format(port)

# query = {
#     "script" : {
#         "source": 'if ( doc.containsKey("content_car_num") ) {ctx._source.content_car_num += 1} else {ctx._source.content_car_num = 1}',
#         "lang": "painless"
#     }
# }

query = {
    "script" : {
        "source": 'ctx._source.content_char_num += 1; ctx._source.content = "test sync update"',
        "lang": "painless"
    }
}

content = json.dumps(query) + "\n"


url = "{}/{}/_update/{}?refresh=true".format(HOST, index, doc_id)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

with httpx.Client(timeout=300) as client:
    init_time = None
    end_time = 0
    while True:
        try:
            # time.sleep(1)
            if init_time is None:
                init_time = time.time()
                start_time = init_time
            else:
                start_time = time.time()
            response = client.post(url, content=content, headers={"Content-Type": "application/json"})
            response_json = response.json()
            log_data.append({"time": int((time.time() - start_time) * 1000),
                             "start time": start_time - init_time})
            if "error" in response_json.keys():
                print(json.dumps(response_json, indent=2))
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            end_time = time.time() - init_time
            break
        except KeyError:
            print("A keyerror occured!")
            print("Response is : {}".format(response_json))
            continue
    
    
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
    
    print(np.mean(throughput_in_sec))
