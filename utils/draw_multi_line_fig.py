import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
sys.path.append('.')

from file_operation import create_file, open_file

# # bulk document
# data_id = ["20231026010309", "20231026010200", "20231026010502", "20231025090203", "20231025090205", "20231026020002"]
# data_label = ["base_w_predict", "base_wo_predict", "moo_w_predict", "moo_wo_predict", "normal", "wo_cancel"]

# # request cache
# data_id = ["20231026010307", "20231026010107", "20231026010407", "20231025080503", "20231025090109", "20231026020000"]
# data_label = ["base_w_predict", "base_wo_predict", "moo_w_predict", "moo_wo_predict", "normal", "wo_cancel"]

# # complex_boolean
# data_id = ["20231101090303", "20231101080503", "20231101090200", "20231101090206", "20231101080507", "20231101090100"]
# data_label = ["base_w_predict", "base_wo_predict", "moo_w_predict", "moo_wo_predict", "normal", "wo_cancel"]

# # update_by_query
# data_id = ["20231101140402", "20231101140509", "20231101150200", "20231101150104", "20231101140407", "20231101150206"]
# data_label = ["base_w_predict", "base_wo_predict", "moo_w_predict", "moo_wo_predict", "normal", "wo_cancel"]

# nest_agg
data_id = ["20231102010108", "20231102010104", "20231102010001", "20231102010009", "20231102010209", "20231102010205"]
data_label = ["base_w_predict", "base_wo_predict", "moo_w_predict", "moo_wo_predict", "normal", "wo_cancel"]

curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

plt.figure(figsize=(10 ,5))
for id, label in zip(data_id, data_label):
    data_file = open_file("data_{}".format(id))
    data_df = pd.read_csv(data_file)
    data_file.close()
    data_list = list(data_df.values[0])
    data_list = data_list[2:]
    plt.plot([x for x in range(len(data_list))], data_list, label=label, linewidth=0.8)

plt.xlabel("Time (s)")
plt.ylabel("Throughput (QPS)")
plt.legend()
fig_file = create_file("fig", "wb", curr_time, ".jpg")
plt.savefig(fig_file)
fig_file.close()
