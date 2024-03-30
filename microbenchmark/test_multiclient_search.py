import json
import os
import signal
import time
import random
import httpx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append('')

from utils.file_operation import create_file

port = 9200
HOST = "http://localhost:{}".format(port)

file_name = sys.argv[1]
indices = sys.argv[2]

log_for_parties = None
if len(sys.argv) > 4:
    log_for_parties = sys.argv[4]

throughput = 0
def signal_handler(signalnum, frame):
    global throughput
    output_file = open(file_name, 'a')
    output_file.write(str(throughput) + "\n")
    output_file.close()
    throughput = 0
    
signal.signal(signal.SIGUSR1, signal_handler)

query = {
    "size": 1,
    "aggs": {
        "histogram_by_char_num_0": {
            "histogram": {
                "field": "content_char_num",
                "interval": 480,
                "min_doc_count": 0
            },
            "aggs": {
                "histogram_by_char_num_1": {
                    "histogram": {
                        "field": "content_char_num",
                        "interval": 640,
                        "min_doc_count": 0
                    },
                    "aggs": {
                        "histogram_by_char_num_2": {
                            "histogram": {
                                "field": "content_char_num",
                                "interval": 549,
                                "min_doc_count": 0
                            },
                            "aggs": {
                                "histogram_by_char_num_3": {
                                    "histogram": {
                                        "field": "content_char_num",
                                        "interval": 527,
                                        "min_doc_count": 0
                                    },
                                    "aggs": {
                                        "histogram_by_char_num_4": {
                                            "histogram": {
                                                "field": "content_char_num",
                                                "interval": 130,
                                                "min_doc_count": 0
                                            },
                                            "aggs": {
                                                "stats_char_num": {
                                                    "stats": {
                                                        "field": "content_char_num"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

url = "{}/{}/_search".format(HOST, indices)

latency_list = []
with httpx.Client(timeout=300) as client:
    while True:
        try:
            query["aggs"]["histogram_by_char_num_0"]["histogram"]["interval"] = random.randint(300, 2000)
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
            throughput += 1
        except KeyboardInterrupt:
            latency_file = open(sys.argv[3], "w")
            for latency in latency_list[1:]:
                latency_file.write(str(latency) + "\n")
            latency_file.close()
            print("Recieve keyboard interrupt from user, break")
            break
        except KeyError:
            print("A keyerror occured!")
            continue
