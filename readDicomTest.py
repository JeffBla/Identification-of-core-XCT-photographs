from pydicom import dcmread
from pydicom.pixel_data_handlers.util import convert_color_space
import cv2
import numpy as np
import matplotlib.pyplot as plt

from config import config

with open(config['filePathOrigin'] + '/24002472', 'rb') as f:
    ds = dcmread(f)
    with open('dsInfo.txt', 'w') as tf:
        tf.write(str(ds))
    # print(ds.PhotometricInterpretation)
    # arr = ds.pixel_array
    # arr[arr > 100] = 300
    # ds.PixelData = arr.tobytes()
    # print(ds.pixel_array)
    # print(ds.PhotometricInterpretation)
    plt.imshow(ds.pixel_array)
    plt.show()
