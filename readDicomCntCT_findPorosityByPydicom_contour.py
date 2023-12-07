from pydicom import dcmread
import cv2 as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
    parser.add_argument("--CTG",
                        type=float,
                        default=1096,
                        help="size of the batches")
    parser.add_argument(
        '--isDraw',
        action=argparse.BooleanOptionalAction,
        help='Show images contain circle ,contour and porosity.')
    parser.add_argument("--csv_output",
                        type=str,
                        default='csv_output.csv',
                        help="the target of csv file to output")

    args = parser.parse_args()
    return args.inDirname, args.CTG, args.isDraw, args.csv_output


def show_brightness(event, x, y, flags, userdata):
    if (event == cv.EVENT_LBUTTONDOWN):
        # test the x,y position in img array
        # img[y, x] = 255
        # cv.imshow('test', img)

        # there is a trick that img[a,b] -> corresponse to x->b, y->a in picture
        print(f"x: {x}, y: {y}, Hu: {Hu[y,x]}, color: {img[y,x]}")


inDirname, CTG, isDraw, csv_output_filename = get_program_parameters()

files = os.listdir(inDirname)
porosityList = np.array([])
for idx, filename in enumerate(files):
    with open(Path(inDirname, filename), 'rb') as f:
        ds = dcmread(f)

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

        img = cv.medianBlur(o8, 5)
        cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

        # area finding
        # Threshold the image to create a binary image
        ret, thresh = cv.threshold(img, 100, 255, cv.THRESH_BINARY)
        contours, hierarchy = cv.findContours(thresh, 2, 1)

        cnt = contours
        big_contour = []
        max = 0
        for i in cnt:
            area = cv.contourArea(
                i)  #--- find the contour having biggest area ---
            if (area > max):
                max = area
                big_contour = i

        # collect all the CT value in contour
        HuList = np.array([])
        for idx, j in np.ndenumerate(Hu):
            # check is inside the coutour?
            # pointPolygonTest -> positive (inside), negative (outside), or zero (on an edge)
            if (cv.pointPolygonTest(big_contour, (idx[1], idx[0]), False) > 0):
                HuList = np.append(HuList, Hu[idx[0], idx[1]])
        if HuList.size != 0:
            # calculate porosity
            numOfVoxelLowerZero = 0
            circleHuList_weight = np.array([])
            for ct in HuList:
                if ct < 0:
                    numOfVoxelLowerZero += 1
                elif ct < CTG:
                    circleHuList_weight = np.append(circleHuList_weight, ct)

            if circleHuList_weight.size != 0:
                circleVwList = (CTG - circleHuList_weight) / CTG
                porosity = (circleVwList.sum() +
                            numOfVoxelLowerZero) / HuList.size
                # print(porosity)
                porosityList = np.append(porosityList, porosity)
            else:
                porosityList = np.append(porosityList, 0)
                print('circleHuList_weight is empty.')
        else:
            porosityList = np.append(porosityList, 0)
            print('HuList is empty.')

        # matplotlib view
        # fig, axes = plt.subplots(2)
        # counts, bins = np.histogram(circleHuList, 100)
        # axes[0].hist(bins[:-1], bins, weights=counts)

        # counts, bins = np.histogram(circleVwList, 100)
        # axes[1].hist(bins[:-1], bins, weights=counts)\

        # plt.show()

        # plotly view
        # fig = make_subplots(2)
        # fig.append_trace(go.Histogram(x=circleHuList, name='Hu'), row=1, col=1)

        # fig.append_trace(go.Histogram(x=circleVwList, name='Vw'), row=2, col=1)

        # fig.show()

        # show image
        if isDraw:
            cv.imshow('detected circles', cimg)
            # cv.imshow('img', thresh)
            # cv.imshow('imgCanny', imgCanny)
            cv.setMouseCallback('detected circles', show_brightness)
            cv.waitKey(0)
            cv.destroyAllWindows()

totalPorotisy = porosityList.sum() / len(porosityList)

df = pd.DataFrame(porosityList)
df.to_csv(csv_output_filename)

print(totalPorotisy)
