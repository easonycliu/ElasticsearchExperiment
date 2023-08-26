import os
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('.')

from utils.file_operation import create_file

if __name__ == "__main__":
    file_name = "corerequest2023-08-24-22-26-54.log"
    keyword = "Cancellable group with root Cancellable ID"
    resource_type = "CPU"
    cancellable_id = "17843"
    timestamp_keyword = "Current time"
    start_time = 1692887225214
    
    log_file_path = os.path.join(os.getcwd(), "autocancel_log", file_name)
    log_file = open(log_file_path, "r")
    root_resource_timestamp_dict = {}
    line_buffer = []
    current_time = 0
    for line in log_file:
        if "Current time" in line:
            current_time = int(line.split(" ")[2])
            root_resource_timestamp_dict[current_time] = {"burst": 0.0, "others": 0.0}
        else:
            if keyword in line and resource_type in line:
                if cancellable_id in line:
                    root_resource_timestamp_dict[current_time]["burst"] = float(line.split(' ')[11][:-1])
                else:
                    root_resource_timestamp_dict[current_time]["others"] += float(line.split(' ')[11][:-1])

    # print(root_resource_timestamp_dict)
    log_file.close()

    fig = create_file("fig", "wb", sufix=".jpg")
    time = list(root_resource_timestamp_dict.keys())
    burst_task = [root_resource_timestamp_dict[key]["burst"] for key in time]
    others_task = [root_resource_timestamp_dict[key]["others"] for key in time]
    total_task = [x + y for x, y in zip(burst_task, others_task)]
    
    plt.plot([x - start_time for x in time], burst_task, label="Burst task")
    plt.plot([x - start_time for x in time], others_task, label="Others tasks")
    # plt.plot([x - start_time for x in time], total_task, label="Overall task")
    plt.xlabel("Time in milli")
    plt.ylabel("CPU usage")
    plt.legend()
    plt.ylim((0))
    plt.xlim((0))
    plt.savefig(fig)
    fig.close()
    
            