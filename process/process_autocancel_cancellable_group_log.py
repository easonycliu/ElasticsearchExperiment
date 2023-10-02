import os
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
sys.path.append('.')

from utils.file_operation import create_file

if __name__ == "__main__":
    file_name = "cancellable_group2023-09-11-05-16-05.log"
    cancellable_id = "9498"
    monitoring_resource = "MEMORY"
    start_time = 1694380663790
    
    log_file_path = os.path.join(os.getcwd(), "autocancel_log", file_name)
    log_file = open(log_file_path, "r")
    
    log_file_timestamp_dict = {}
    is_monitored_resource = False
    
    for line in log_file:
        if "Current time:" in line:
            current_time = int(line.split(" ")[2])
            log_file_timestamp_dict[current_time] = {"burst": 0, "others": 0}
            continue
        if "Root Cancellable ID :" in line and line.split(" ")[4] == cancellable_id:
            is_monitored_resource = True
            continue
        if "Resource Type:" in line and monitoring_resource in line:
            if float(line.split(" ")[7][:-1]) == 0:
                continue
            
            if is_monitored_resource:
                log_file_timestamp_dict[current_time]["burst"] = float(line.split(" ")[10][:-1])
                is_monitored_resource = False
            else:
                log_file_timestamp_dict[current_time]["others"] += float(line.split(" ")[10][:-1])
            continue
        
    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    fig = create_file("fig", "wb", time_str, sufix=".jpg")
    time = list(log_file_timestamp_dict.keys())
    burst_task = [log_file_timestamp_dict[key]["burst"] / 1000000000000 for key in time]
    others_task = [log_file_timestamp_dict[key]["others"] / 1000000000000 for key in time]
    total_task = [x + y for x, y in zip(burst_task, others_task)]
    
    plt.plot([(x - start_time) / 1000 for x in time], burst_task, label="Burst task")
    plt.plot([(x - start_time) / 1000 for x in time], others_task, label="Others tasks")
    # plt.plot([x - start_time for x in time], total_task, label="Overall task")
    plt.xlabel("Time (s)")
    plt.ylabel("Memory usage (Tera Bytes)")
    plt.legend()
    plt.ylim((0))
    plt.xlim((0, 60))
    plt.savefig(fig)
    fig.close()
    plt.close()