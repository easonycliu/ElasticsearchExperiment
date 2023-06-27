import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('')

from utils.file_operation import open_file
from process.utils.raise_time import raise_time

NORMAL_DATA_THRESHOLD = 50

def draw_cancel_to_perf(file_name_log_name):
    file_name_log_file = open_file(file_name_log_name, False)
    file_name_log_df = pd.read_csv(file_name_log_file, sep=" ", header=None, index_col=0)
    
    stat_dict = {}
    for cancel_after_burst in file_name_log_df.index:
        raise_time_list = []
        avg_throughput_list = []
        for file_name in file_name_log_df.loc[cancel_after_burst]:
            try:
                data_file = open_file("data_{}".format(file_name))
                data_df = pd.read_csv(data_file, sep=",")
                data_file.close()
                data_list = data_df.values.tolist()[0]
                if len(data_list) < NORMAL_DATA_THRESHOLD:
                    continue
                
                raise_time_list.append(raise_time(data_list))
                avg_throughput_list.append(np.mean(data_list))
            except FileNotFoundError:
                print("data_{} Not Found".format(file_name))
                continue
            
        stat_dict[cancel_after_burst] = {"raise_time": np.mean(raise_time_list), "avg_throughput": np.mean(avg_throughput_list)}
            
    file_name_log_file.close()

    plt.plot(list(stat_dict.keys()), [stat_dict[cancel_time]["avg_throughput"] for cancel_time in stat_dict.keys()], marker="^")
    plt.xlabel("Cancel Time (s)")
    plt.ylabel("Avg Throughput (Number of Requests)")
    plt.savefig(os.path.join(os.getcwd(), "fig", "fig_avg_throughput_{}.jpg".format(file_name_log_name.split("_")[-1])))
    plt.close()
    
    plt.plot(list(stat_dict.keys()), [stat_dict[cancel_time]["raise_time"] for cancel_time in stat_dict.keys()], marker="^")
    plt.xlabel("Cancel Time (s)")
    plt.ylabel("Raise Time (s)")
    plt.savefig(os.path.join(os.getcwd(), "fig", "fig_raise_time_{}.jpg".format(file_name_log_name.split("_")[-1])))

if __name__ == "__main__":
    draw_cancel_to_perf("log_20230625072957")
    