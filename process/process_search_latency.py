import os
import matplotlib.pyplot as plt

from utils.data_filter import avg_filter
from utils.read_response import read_response

if __name__ == "__main__":
    response_name = "response_20230606053213"
    data = read_response(response_name, lambda x : int(x.split(" ")[3][:-1]))
    filtered_data = avg_filter(data, 20)
    plt.plot([x for x in range(len(filtered_data))], data[:len(filtered_data)], label="Origin")
    plt.plot([x for x in range(len(filtered_data))], filtered_data, label="Filtered")
    plt.legend()
    plt.savefig(os.path.join(os.getcwd(), "fig", "fig_{}.jpg".format(response_name)))
    