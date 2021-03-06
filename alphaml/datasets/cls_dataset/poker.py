import numpy as np


def load_poker(data_folder):
    # The dataset contains more than 1M samples. We use only 50000 of them.
    L = []
    file_path = data_folder + 'poker'
    with open(file_path, 'r') as f:
        for line in f.readlines():
            items = line.split('\n')[0].split(' ')
            l = [0] * 11
            l[0] = int(items[0])
            for item in items[1:]:
                if len(item.split(':')) < 2:
                    continue
                index, val = item.split(':')
                l[int(index)] = int(val)
            L.append(l)
    data = np.array(L)
    return data[:50000, 1:], data[:50000, 0]
