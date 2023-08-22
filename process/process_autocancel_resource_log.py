import os
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('.')

from utils.file_operation import create_file

def get_child_cancellable_id(log_file_dict, keyword, parent_id):
    cancellable_ids = []
    for key in log_file_dict.keys():
        lines = log_file_dict[key]
        for line in lines:
            if keyword in line and parent_id in line:
                items = line.split(" ")
                cancellable_ids.append(items[4])
    return cancellable_ids

if __name__ == "__main__":
    file_name = "corerequest2023-08-08-20-44-51.log"
    keyword = "search"
    cancellable_id = "1180"
    
    log_file_path = os.path.join(os.getcwd(), "autocancel_log", file_name)
    log_file = open(log_file_path, "r")
    log_file_timestamp_dict = {}
    line_buffer = []
    current_time = 0
    for line in log_file:
        if "Current time" not in line and len(log_file_timestamp_dict) == 0:
            continue
        if "Current time" in line:
            current_time = int(line.split(" ")[2])
            log_file_timestamp_dict[current_time] = []
        else:
            log_file_timestamp_dict[current_time].append(line)
    resource_usage_dict = {}
    resource_usage_parent_dict = {}
    cancellable_ids = get_child_cancellable_id(log_file_timestamp_dict, keyword, cancellable_id)
    print(cancellable_ids)
    for timestamp in sorted(list(log_file_timestamp_dict.keys())):
        for line in log_file_timestamp_dict[timestamp]:
            if "UPDATE" in line and "CPU" in line:
                id = line.split(" ")[4]
                if id == cancellable_id:
                    resource_usage_parent_dict[timestamp] = float(line.split(" ")[7].split(";")[0])
                if id in cancellable_ids:
                    resource_usage = float(line.split(" ")[7].split(";")[0])
                    if timestamp in resource_usage_dict.keys():
                        resource_usage_dict[timestamp] += resource_usage
                    else:
                        resource_usage_dict[timestamp] = resource_usage

    time = []
    resource_overall = []
    resource_parent = []
    for timestamp in sorted(list(resource_usage_dict.keys())):
        if resource_usage_dict[timestamp] > 0.0:
            time.append(timestamp)
            resource_overall.append(resource_usage_dict[timestamp])
            if timestamp in resource_usage_parent_dict.keys():
                resource_parent.append(resource_usage_parent_dict[timestamp])
            else:
                resource_parent.append(0.0)
            print("Time: {} ; Resource: {}".format(timestamp, resource_usage_dict[timestamp]))
    
    log_file.close()

    fig = create_file("fig", "wb", sufix=".jpg")
    plt.plot([x - np.min(time) for x in time], resource_overall, label="All tasks")
    plt.plot([x - np.min(time) for x in time], resource_parent, label="Parent task")
    plt.xlabel("Time in milli")
    plt.ylabel("CPU usage")
    plt.legend()
    plt.ylim((0))
    plt.savefig(fig)
    fig.close()
    
            