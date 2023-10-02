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

index = sys.argv[1]
doc_id = sys.argv[2]
port = 9200
HOST = "http://localhost:{}".format(port)

creator_number = 1

file_name = sys.argv[3]

throughput = 0

def signal_handler(signalnum, frame):
    global throughput
    # print("Recieve {} at frame {}".format(signalnum, frame))
    output_file = open(file_name, 'a')
    output_file.write(str(throughput) + "\n")
    output_file.close()
    throughput = 0
signal.signal(signal.SIGUSR1, signal_handler)

query = {
    "script" : {
        "source": 'ctx._source.content_char_num += 1; ctx._source.content = "test sync update"',
        "lang": "painless"
    }
}
            
url = "{}/{}/_update/{}?refresh=true".format(HOST, index, doc_id)
    
client = httpx.Client(timeout=300000)
while True:
    try:
        content = json.dumps(query) + "\n"
        response = client.post(url, content=content, headers={"Content-Type": "application/json"})
        response_json = response.json()
        if "error" in response_json.keys():
            print("An error occored in sender {}, {}!".format(id, response_json["error"]))
            continue
        throughput += 1
    except KeyboardInterrupt:
        print("Recieve keyboard interrupt from user, break")
        break

client.close()
