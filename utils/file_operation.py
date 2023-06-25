import os
import time

def create_file(type, option, time_str=None):
    time_tuple = time.localtime(time.time()) if time_str is None else time.strptime(time_str, "%Y%m%d%H%M%S")
    curr_day = time.strftime("%Y%m%d", time_tuple)
    curr_time = time.strftime("%Y%m%d%H%M%S", time_tuple)
    file_path = os.path.join(os.getcwd(), type, curr_day)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = os.path.join(file_path, "{}_{}".format(type, curr_time))
    return open(file_name, option)

def open_file(name):
    local_time_struct = time.strptime(name.split("_")[-1], "%Y%m%d%H%M%S")
    local_day_string = time.strftime("%Y%m%d", local_time_struct)
    file_name = os.path.join(os.getcwd(), name.split("_")[0], local_day_string, name)
    return open(file_name, "r")
