# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkIOImage import vtkDICOMImageReader

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
    parser.add_argument(
        '--isDraw',
        action=argparse.BooleanOptionalAction,
        help='Show images contain circle ,contour and porosity.')

    args = parser.parse_args()
    return args.inDirname, args.isDraw


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
        print(f"x: {x}, y: {y}, Hu: {Hu[y,x]}, color: {img[y,x]}")


inDirname, isDraw = get_program_parameters()

reader = vtkDICOMImageReader()
reader.SetDirectoryName(inDirname)
reader.Update()

files = os.listdir(inDirname)

dcmImage_CT = np.array(reader.GetOutput().GetPointData().GetScalars()).reshape(
    len(files), reader.GetHeight(), reader.GetWidth())

porosityList = np.array([])
for index, filename in enumerate(files):
    # print("正常的或被压缩的：" + reader.GetTransferSyntaxUID())
    # print(f"Rescale Slope: {reader.GetRescaleSlope()}")
    # print(f"Rescale Intercept: {reader.GetRescaleOffset()}")
    # print("The formula of CT value: Hu = pixel * slope + intercept")
    # with open('dsInfo.txt', 'w') as tf:
    #     tf.write(str(ds))

    # 提取像素數據
    # CT value
    Hu = np.flipud(dcmImage_CT[index])

    px_arr = (Hu - reader.GetRescaleOffset()) / reader.GetRescaleSlope()

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
    img = o8
    cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    imgCanny = cv.Canny(img, 30, 150)

    circles = cv.HoughCircles(imgCanny,
                              cv.HOUGH_GRADIENT,
                              2,
                              20,
                              param1=70,
                              param2=90,
                              minRadius=110,
                              maxRadius=130)

    # area finding
    # Threshold the image to create a binary image
    ret, thresh = cv.threshold(img, 100, 255, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(thresh, 2, 1)

    cnt = contours
    big_contour = []
    max = 0
    for i in cnt:
        area = cv.contourArea(i)  #--- find the contour having biggest area ---
        if (area > max):
            max = area
            big_contour = i

    # Inside circles
    fluidPercentList = np.array([])
    if circles is not None:
        circles = np.uint16(np.around(circles))

        # Sometimes, I will many cycles in a image.
        # The way I choose is based on the y vale
        # I choose the topest of the center of circle.
        argmax = np.argmin(circles[0, :, 1])

        circle = circles[0, argmax]

        # calculate porosity
        circleHuList = np.array([])
        for idx, j in np.ndenumerate(Hu):
            # check is inside the circle and coutour?
            # pointPolygonTest -> positive (inside), negative (outside), or zero (on an edge)
            if (checkInCircle(circle[0], circle[1], circle[2] - shrinkToCenter,
                              idx[1], idx[0])
                    and (cv.pointPolygonTest(big_contour,
                                             (idx[1], idx[0]), False) > 0)):
                circleHuList = np.append(circleHuList, Hu[idx[0], idx[1]])

        for Hu_element in circleHuList:
            constMat = np.array([Hu_element, 1])
            uPlus2S = 1095
            coefMat = np.array([[uPlus2S, -1000], [1, 1]])
            varMat = np.linalg.inv(coefMat) @ constMat
            # get the percent of solid
            solidPercent = varMat[0]
            fluidPercentList = np.append(fluidPercentList, 1 - solidPercent)

        if fluidPercentList.size != 0:
            porosity = fluidPercentList.sum() / len(fluidPercentList)
            print(porosity)
            porosityList = np.append(porosityList, porosity)
        else:
            print('fluidPercentList is empty.')

    # matplotlib view)
    # fig, axes = plt.subplots(2)
    # counts, bins = np.histogram(circleHuList, 100)
    # axes[0].hist(bins[:-1], bins, weights=counts)

    # counts, bins = np.histogram(circleVwList, 100)
    # axes[1].hist(bins[:-1], bins, weights=counts)\

    # plt.show()

    # plotly view
    # fig = make_subplots(1)
    # fig.append_trace(go.Histogram(x=circleHuList, name='Hu'), row=1, col=1)

    # 3d visualize Hu by ployly
    # sh_0, sh_1 = Hu.shape
    # x, y = np.linspace(0, 1, sh_0), np.linspace(0, 1, sh_1)

    # fig = go.Figure(data=[go.Surface(z=Hu, x=y, y=x)])
    # fig.update_traces(contours_z=dict(show=True,
    #                                   usecolormap=True,
    #                                   highlightcolor="limegreen",
    #                                   project_z=True))
    # fig.show()

    # show image
    if isDraw:
        if circles is not None:
            # draw the outer circle
            cv.circle(cimg, (circle[0], circle[1]), circle[2] - shrinkToCenter,
                      (0, 0, 255), 2)
            # draw the center of the circle
            cv.circle(cimg, (circle[0], circle[1]), 2, (0, 0, 255), 3)

            cv.drawContours(cimg, big_contour, -1, (0, 255, 0), 2)
            cv.putText(cimg, f'{porosity}', (0, 45), cv.FONT_HERSHEY_SIMPLEX,
                       config['imgTextFontScale'], config['imgTextColor'],
                       config['imgTextThickness'], cv.LINE_AA)
            print(f"{filename}'s porosity: {porosity}")

        cv.imshow('detected circles', cimg)
        # cv.imshow('img', thresh)
        # cv.imshow('imgCanny', imgCanny)
        cv.setMouseCallback('detected circles', show_brightness)
        cv.waitKey(0)
        cv.destroyAllWindows()

print(porosityList.sum() / len(porosityList))
