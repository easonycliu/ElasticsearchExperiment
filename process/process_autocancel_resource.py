import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
sys.path.append('.')

from utils.file_operation import create_file

def get_task_resource_usage(file_name, keyword, resource_type, cancellable_id, data_position):
    log_file_path = os.path.join(os.getcwd(), "autocancel_log", file_name)
    log_file = open(log_file_path, "r")
    root_resource_timestamp_dict = {}
    current_time = 0
    for line in log_file:
        if "Current time" in line:
            current_time = int(line.split(" ")[2])
            root_resource_timestamp_dict[current_time] = {"burst": 0.0, "other": 0.0}
        else:
            if keyword in line and resource_type in line:
                if cancellable_id in line:
                    root_resource_timestamp_dict[current_time]["burst"] += float(line.split(' ')[data_position])
                else:
                    root_resource_timestamp_dict[current_time]["other"] += float(line.split(' ')[data_position])
    log_file.close()
    return root_resource_timestamp_dict

def get_resource_info(file_name, keyword, resource_type, data_position):
    log_file_path = os.path.join(os.getcwd(), "autocancel_log", file_name)
    log_file = open(log_file_path, "r")
    root_resource_timestamp_dict = {}
    current_time = 0
    for line in log_file:
        if "Current time" in line:
            current_time = int(line.split(" ")[2])
            root_resource_timestamp_dict[current_time] = 0.0
        else:
            if keyword in line and resource_type in line:
                root_resource_timestamp_dict[current_time] += float(line.split(' ')[data_position])
                    
    log_file.close()
    return root_resource_timestamp_dict

if __name__ == "__main__":
    file_name = "corerequest2023-08-29-00-19-17.log"
    keyword = "Cancellable group with root Cancellable ID"
    resource_type = ""
    cancellable_id = "1741526"
    
    start_time = 1693239562990
    
    root_resource_timestamp_dict = get_task_resource_usage(file_name, 
                                                           "Cancellable group with root Cancellable ID", 
                                                           resource_type, 
                                                           cancellable_id, 
                                                           11)

    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    fig = create_file("fig", "wb", time_str, sufix=".jpg")
    time = list(root_resource_timestamp_dict.keys())
    burst_task = [root_resource_timestamp_dict[key]["burst"] for key in time]
    others_task = [root_resource_timestamp_dict[key]["other"] for key in time]
    total_task = [x + y for x, y in zip(burst_task, others_task)]
    
    plt.plot([x - start_time for x in time], burst_task, label="Burst task")
    plt.plot([x - start_time for x in time], others_task, label="Others tasks")
    # plt.plot([x - start_time for x in time], total_task, label="Overall task")
    plt.xlabel("Time in milli")
    plt.ylabel("Shard locks occupy time")
    plt.legend()
    plt.ylim((0))
    plt.xlim((0))
    plt.savefig(fig)
    fig.close()
    plt.close()
    
    resource_info_name = "Total wait time"
    overall_resource_timestamp_dict = get_resource_info(file_name, 
                                                        "Total wait time", 
                                                        resource_type,
                                                        11)
    fig = create_file("fig", "wb", str(int(time_str) + 1), sufix=".jpg")
    time = list(overall_resource_timestamp_dict.keys())
    resource_info = [overall_resource_timestamp_dict[key] for key in time]
    
    plt.plot([x - start_time for x in time], resource_info, label=resource_info_name)
    # plt.plot([x - start_time for x in time], total_task, label="Overall task")
    plt.xlabel("Time in milli")
    plt.ylabel("Shard locks waiting time")
    plt.legend()
    plt.ylim((0))
    plt.xlim((0))
    plt.savefig(fig)
    fig.close()
    
    