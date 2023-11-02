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

port = 9200
HOST = "http://localhost:{}".format(port)
index = "test4"

file_name = sys.argv[1]
file_name_sync = sys.argv[2]

throughput = 0
def siguser1_handler(signalnum, frame):
    global throughput
    output_file = open(file_name, 'a')
    output_file.write(str(throughput) + "\n")
    output_file.close()
    throughput = 0
signal.signal(signal.SIGUSR1, siguser1_handler)

start = False
def siguser2_handler(signalnum, frame):
    global start
    print("Recieve {} at frame {}".format(signalnum, frame))
    start = True
signal.signal(signal.SIGUSR2, siguser2_handler)

data_buffer = Queue(maxsize=2000)
while not data_buffer.full():
    data_buffer.put(fast_create_a_rubbish())
print("Documents are ready!")
output_sync_file = open(file_name_sync, 'a')
output_sync_file.write("Documents are ready!\n")
output_sync_file.close()

while not start:
    time.sleep(0.1)

url = "{}/{}/_doc?refresh=false".format(HOST, index)

try:
    client = httpx.Client(timeout=300000)
    while True:
        query = data_buffer.get()
        # print("Sender {} sending a new update request, current buffer size is {}".format(id, data_buffer.qsize()))
        content = json.dumps(query) + "\n"
        response = client.post(url, content=content, headers={"Content-Type": "application/json"})
        response_json = response.json()
        if "error" in response_json.keys():
            print("An error occored in sender {}, {}!".format(id, response_json["error"]))
        throughput += 1
except KeyboardInterrupt:
    client.close()
    print("Recieve keyboard interrupt from user, break")
    