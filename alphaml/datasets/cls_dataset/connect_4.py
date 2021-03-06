import numpy as np


def load_connect_4(data_folder):
    L = []
    file_path = data_folder + 'connect-4'
    with open(file_path, 'r') as f:
        for line in f.readlines():
            items = line.strip().split('\n')[0].split(' ')
            d = [0] * 127
            d[0] = int(items[0]) + 1
            for item in items[1:]:
                key, value = item.split(':')
                d[int(key)] = float(value)
            L.append(d)
        data = np.array(L)
        return data[:, 1:], data[:, 0]
