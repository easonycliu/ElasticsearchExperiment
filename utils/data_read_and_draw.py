import matplotlib.pyplot as plt
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

fig_file = create_file("fig", "wb", curr_time, ".jpg")
plt.savefig(fig_file)
fig_file.close()
