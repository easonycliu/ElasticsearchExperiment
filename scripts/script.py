import os
import subprocess
from threading import Thread
import time

def maintain_subprocess(id):
    print("Thread {} start".format(id))
    os.chdir("/root")
    while True:
        result = subprocess.run("python performance_issues/aggregation_intensive_heap_small.py", shell=True)
        if result.returncode == -2:
            print("Thread {} interrupted by user, break".format(id))
            break
        time.sleep(0.1)
        print("Thread {} restart".format(id))
    
if __name__ == "__main__":
    thread_num = 1
    thread_pool = []
    try:
        for i in range(thread_num):
            thread_pool.append(Thread(target=maintain_subprocess, args=[i]))
            thread_pool[i].start()
            time.sleep(1)

        while True:
            pass
    except KeyboardInterrupt:
        for thread in thread_pool:
            thread.join()
        print("Receive keyboard interrupt from user, exit.")
        
        
        