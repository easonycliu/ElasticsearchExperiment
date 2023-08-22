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

port = 9200 if len(sys.argv) < 3 else sys.argv[2]
HOST = "http://localhost:{}".format(port)

query = {
    "query": {
        "match": {
            "content": "life"
        }
    }
}
content = json.dumps(query) + "\n"

only_local = "" if len(sys.argv) < 3 else "&preference=_only_local"
url = "{}/_search?from=0&size=100{}".format(HOST, only_local)
log_data = []

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) if len(sys.argv) == 1 else sys.argv[1]
curr_time = curr_time + str("" if len(sys.argv) < 3 else port)
f = create_file("response", "w", curr_time)

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
                             "start time": start_time - init_time,
                             "result": response_json["hits"]["hits"][0]["_source"]["title"]})
            f.write("time used : {}, start time : {}, result : {}\n".format(log_data[-1]["time"], log_data[-1]["start time"], log_data[-1]["result"]))
            f.flush()
            
        except KeyboardInterrupt:
            print("Recieve keyboard interrupt from user, break")
            end_time = time.time() - init_time
            break
        except KeyError:
            print("A keyerror occured!")
            print("Response is : {}".format(response_json))
            continue
    
    f.close()
    
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
