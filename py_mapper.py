import cv2
import numpy as np

def load_map(map_size: tuple, file_name):
    image = cv2.imread(file_name)
    map_pixels = image.reshape(-1, 3).tolist()
    py_map = []
    index = 0
    for i in range(map_size[1]):
        py_map.append([])
        for j in range(map_size[0]):
            py_map[i].append(map_pixels[index])
            index += 1
    return py_map