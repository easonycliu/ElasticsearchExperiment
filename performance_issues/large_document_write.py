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

if __name__ == "__main__":
    if len(sys.argv) == 3:
        target_length = int(sys.argv[1])
        file_name = sys.argv[2]
        
        update_times = 8

        single_length = target_length // update_times + 1

        document = create_a_rubbish()
        content = document["content"]
        content_length = len(content)

        replicate_times = single_length // content_length + 1

        replicate_content = ""
        for i in range(replicate_times):
            replicate_content += content

        header = { "index" : { "_index" : "large", "_id" : "114514" } }
        f = open(os.path.join(os.getcwd(), "query", file_name), "w")
        for i in range(update_times):
            f.write(json.dumps(header) + "\n")
            query = {"content_char_num": 1, "content": replicate_content}
            query_str = json.dumps(query) + "\n"
            f.write(query_str)
        f.close()
    else:
        print("Usage: ./large_document_write.py DOCUMEMT_BYTES OUTPUT_NAME")
