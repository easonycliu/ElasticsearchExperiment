import os
import time
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('.')

from utils.file_operation import create_file

def read_from_benchmark(file_name):
    file_path = os.path.join(os.getcwd(), "benchmark_log", file_name)
    file = open(file_path)
    throughput_from_benchmark = []
    for line in file:
        throughput_from_benchmark.append(int(line))
        
    return throughput_from_benchmark

def read_from_autocancel_log(file_name, keyword):
    file_path = os.path.join(os.getcwd(), "autocancel_log", file_name)
    file = open(file_path)
    throughput_timestamp = []
    current_time = 0
    for line in file:
        if "Current time" in line:
            current_time = int(line.split(" ")[2])
        else:
            if current_time != 0 and keyword in line:
                throughput_timestamp.append({"finished_request": int(line.split(' ')[0]),
                                            "start_time": int(line.split(' ')[5]),
                                            "end_time": int(line.split(' ')[7]),
                                            "throughput": float(line.split(' ')[11])})
                
    return throughput_timestamp

def process_autocancel_log_throughput(throughput_timestamp):
    index = 0
    throughput_in_second = []
    while index < len(throughput_timestamp):
        start_time = throughput_timestamp[index]["start_time"]
        throughput = 0
        while index < len(throughput_timestamp) and throughput_timestamp[index]["end_time"] < start_time + 850:
            throughput += throughput_timestamp[index]["finished_request"]
            index += 1
        
        throughput_in_second.append(throughput)
        index += 1
    return throughput_in_second
            

if __name__ == "__main__":
    benchmark_log_file = "throughput"
    autocancel_log_file = "corerequest2023-08-29-04-25-45.log"
    
    keyword = "requests has finish since"
    
    throughput_from_benchmark = read_from_benchmark(benchmark_log_file)
    throughput_timestamp = read_from_autocancel_log(autocancel_log_file, keyword)
    throughput_in_second = process_autocancel_log_throughput(throughput_timestamp)
        
    start_index = 60
    end_index = 190
    throughput_in_second = throughput_in_second[start_index:end_index]
    plt.plot([x for x in range(len(throughput_in_second))], throughput_in_second, label="From AutoCancel")
    plt.plot([x for x in range(len(throughput_from_benchmark))], throughput_from_benchmark, label="From benchmark")
    
    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    fig = create_file("fig", "wb", time_str, sufix=".jpg")
    plt.legend()
    plt.savefig(fig)
    fig.close()
    plt.close()
    