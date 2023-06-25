import numpy as np

def raise_time(throughput_list):
    raise_time = 0
    normal_throughput = 0

    for time in range(1, len(throughput_list)):
        if normal_throughput == 0:
            if throughput_list[time] > np.mean(throughput_list[1:time+1]) * 0.2:
                continue
            else:
                normal_throughput = np.mean(throughput_list[1:time+1])
                raise_time += 1
        else:
            if throughput_list[time] < normal_throughput * 0.8:
                raise_time += 1
            else:
                break
            
    return raise_time