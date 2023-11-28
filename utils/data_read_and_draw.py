import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
sys.path.append('')

from utils.file_operation import create_file

file_name = sys.argv[1]
curr_time = file_name.split("_")[-1]
client_num = int(sys.argv[2])

file = open(file_name)
throughput_in_sec=[]
throughput = 0
line_index = 0
for line in file:
    line = line.strip()
    if len(line) == 0:
        break
    line_index += 1
    throughput += int(line)
    if line_index % client_num == 0:
        throughput_in_sec.append(throughput)
        throughput = 0
    
throughput_in_sec = throughput_in_sec[1:]
plt.plot([x for x in range(len(throughput_in_sec))], throughput_in_sec)
plt.xlabel("Time (s)")
plt.ylabel("Throughput (Number of Requests)")
plt.ylim((0))

print(np.mean(throughput_in_sec))
throughput_file = open(sys.argv[3], "w")
throughput_file.write("Throughput\n")
for throughput_sec in throughput_in_sec:
    throughput_file.write(str(throughput_sec) + "\n")
throughput_file.close()

fig_file = create_file("fig", "wb", curr_time, ".jpg")
plt.savefig(fig_file)
fig_file.close()

throughput_in_sec_df = pd.DataFrame(throughput_in_sec)
f = create_file("data", "w", curr_time)
throughput_in_sec_df.T.to_csv(f, ",")
f.close()
