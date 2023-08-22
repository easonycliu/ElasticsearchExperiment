import os
import time

def create_file(type, option, time_str=None, sufix=""):
    time_tuple = time.localtime(time.time()) if time_str is None else time.strptime(time_str[:12], "%Y%m%d%H%M%S")
    curr_day = time.strftime("%Y%m%d", time_tuple)
    file_path = os.path.join(os.getcwd(), type, curr_day)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = os.path.join(file_path, "{}_{}{}".format(type, time.strftime("%Y%m%d%H%M%S", time_tuple), sufix))
    return open(file_name, option)

def open_file(name, classify_by_day=True):
    local_time_struct = time.strptime(name.split("_")[-1], "%Y%m%d%H%M%S")
    local_day_string = time.strftime("%Y%m%d", local_time_struct) if classify_by_day else ""
    file_name = os.path.join(os.getcwd(), name.split("_")[0], local_day_string, name)
    return open(file_name, "r")
