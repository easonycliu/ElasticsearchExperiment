import os
import signal
from multiprocessing import Process
from threading import Thread
import time
import sys
sys.path.append('')
    
if __name__ == "__main__":

    benchmark_process = Process(target=lambda : os.execve(sys.executable,
                                                          [sys.executable, os.path.join(os.getcwd(), "microbenchmark", "test_sync_search.py")], 
                                                          os.environ))
    print("Start benchmark")
    benchmark_process.start()
    
    time.sleep(10.0)
    
    burst_process = Process(target=lambda : os.execve("/usr/bin/curl", 
                                                      ["/usr/bin/curl",
                                                       "-X",
                                                       "GET",
                                                       "-H",
                                                       "Content-Type:application/json",
                                                       "--data-binary",
                                                       "@{}".format(os.path.join(os.getcwd(), "query", "boolean_search.json")),
                                                       "http://localhost:9200/_search"],
                                                      os.environ))
    print("Start burst client")
    burst_process.start()
    
    time.sleep(10.0)
    
    print("Kill burst client at {} second".format(20.0))
    os.kill(burst_process.pid, signal.SIGINT)
    
    time.sleep(10.0)
    print("Kill benchmark client after {} second".format(30.0))
    os.kill(benchmark_process.pid, signal.SIGINT)
    
    print("Wait for all subprocesses to join")
    benchmark_process.join()
    burst_process.join()
        