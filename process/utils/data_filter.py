import numpy as np

def avg_filter(data, window):
    assert len(data) > window
    filtered_data = []
    for index in range(len(data) - window):
        filtered_data.append(np.mean(data[index : index + window]))
    return filtered_data
