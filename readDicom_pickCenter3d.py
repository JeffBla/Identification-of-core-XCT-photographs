from pydicom import dcmread
import cv2 as cv
import numpy as np
import pandas as pd

import os
from pathlib import Path

from config import config

shrinkToCenter = 0


def get_program_parameters():
    import argparse
    description = 'Align the center of target cycle, and output the dicom image cut by the target cycle.'
    epilogue = '''
 Output folder default is dcmCutCycleOut.
     '''
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilogue,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'inDirname',
        help=
        'The target dir only contain dicom files, and all files in the dir will be read.'
    )
    parser.add_argument('-outDirname',
                        default='./dcmCutCycleOut',
                        help='The output dicom files are stored here')
    parser.add_argument(
        '--isDraw',
        action=argparse.BooleanOptionalAction,
        help='Show images contain circle ,contour and porosity.')

    args = parser.parse_args()
    return args.inDirname, args.outDirname, args.isDraw


def checkInCircle(cx, cy, r, idxX, idxY) -> bool:
    if (idxX - cx)**2 + (idxY - cy)**2 < r**2:
        return True
    else:
        return False


def show_brightness(event, x, y, flags, userdata):
    if (event == cv.EVENT_LBUTTONDOWN):
        # test the x,y position in img array
        # img[y, x] = 255
        # cv.imshow('test', img)

        # there is a trick that img[a,b] -> corresponse to x->b, y->a in picture
        print(f"x: {x}, y: {y}, color: {Hu[y,x]}")


inDirname, outDirname, isDraw = get_program_parameters()

files = os.listdir(inDirname)
for filename in files:
    with open(Path(inDirname, filename), 'rb') as f:
        ds = dcmread(f)
        # print("正常的或被压缩的：" + ds.file_meta.TransferSyntaxUID.name)
        # print(f"Rescale Slope: {ds.RescaleSlope}")
        # print(f"Rescale Intercept: {ds.RescaleIntercept}")
        # print("The formula of CT value: Hu = pixel * slope + intercept")
        # with open('dsInfo.txt', 'w') as tf:
        #     tf.write(str(ds))

        # 提取像素數據
        px_arr = np.array(ds.pixel_array)
        # CT value
        Hu = px_arr * ds.RescaleSlope + ds.RescaleIntercept

        # # rescale original 16 bit image to 8 bit values [0,255]
        x0 = np.min(px_arr)
        x1 = np.max(px_arr)
        y0 = 0
        y1 = 255.0
        i8 = ((px_arr - x0) * ((y1 - y0) / (x1 - x0))) + y0

        # # create new array with rescaled values and unsigned 8 bit data type
        o8 = i8.astype(np.uint8)

        # print(f"rescaled data type={o8.dtype}")

        # do the Hough transform
        img = cv.medianBlur(o8, 5)
        cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        imgCanny = cv.Canny(img, 30, 150)

        # erode
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        imgErode = cv.erode(img, kernel)

        circles = cv.HoughCircles(imgCanny,
                                  cv.HOUGH_GRADIENT,
                                  2,
                                  40,
                                  param1=70,
                                  param2=95,
                                  minRadius=110,
                                  maxRadius=130)

        # Inside circles
        if circles is not None:
            circles = np.uint16(np.around(circles))

            # Sometimes, I will many cycles in a image.
            # The way I choose is based on the y vale
            # I choose the topest of the center of circle.
            argmax = np.argmin(circles[0, :, 1])

            circle = circles[0, argmax]

            # output circle dicom file matched center for 3d
            circle_px_arr = px_arr
            target_row = circle[1] - config['cutCycleRadius']
            target_col = circle[0] - config['cutCycleRadius']
            circle_px_arr = circle_px_arr[target_row:target_row +
                                          2 * config['cutCycleRadius'],
                                          target_col:target_col +
                                          2 * config['cutCycleRadius']]
            ds.PixelData = circle_px_arr.tobytes()
            ds.Rows = circle_px_arr.shape[0]
            ds.Columns = circle_px_arr.shape[1]
            ds.save_as(Path(outDirname, filename))

        # show image
        if isDraw:
            if circles is not None:
                # draw the outer circle
                cv.circle(cimg, (circle[0], circle[1]),
                          circle[2] - shrinkToCenter, (0, 0, 255), 2)
                # draw the center of the circle
                cv.circle(cimg, (circle[0], circle[1]), 2, (0, 0, 255), 3)

            cv.imshow('detected circles', cimg)
            # cv.imshow('img', img)
            # cv.imshow('imgErode', imgErode)
            cv.setMouseCallback('detected circles', show_brightness)
            cv.waitKey(0)
            cv.destroyAllWindows()
