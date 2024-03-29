from pydicom import dcmread
import cv2 as cv
import numpy as np
import pandas as pd

import os
from pathlib import Path

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
                        default='./dcmCutCycleOut_copy',
                        help='The output dicom files are stored here')
    parser.add_argument('-imgSize',
                        default=512,
                        type=int,
                        help='Set the size of output img')
    parser.add_argument(
        '--isDraw',
        action=argparse.BooleanOptionalAction,
        help='Show images contain circle ,contour and porosity.')
    parser.add_argument('--isCrop',
                        action=argparse.BooleanOptionalAction,
                        help='Crop the image to the imgSize.')
    parser.add_argument('--isTwice',
                        action=argparse.BooleanOptionalAction,
                        help='Append the image, width x2, to feed the pix2pix')

    args = parser.parse_args()
    return args.inDirname, args.outDirname, args.imgSize, args.isDraw, args.isCrop, args.isTwice


def show_brightness(event, x, y, flags, userdata):
    if (event == cv.EVENT_LBUTTONDOWN):
        # test the x,y position in img array
        # img[y, x] = 255
        # cv.imshow('test', img)

        # there is a trick that img[a,b] -> corresponse to x->b, y->a in picture
        print(f"x: {x}, y: {y}, color: {Hu[y,x]}")


inDirname, outDirname, IMAGE_SIZE, isDraw, isCrop, isTwice = get_program_parameters(
)

files = os.listdir(inDirname)
# set the study instance UID equally
with open(Path(inDirname, files[0]), 'rb') as f:
    ds = dcmread(f)
    file_SeriesInstanceUID = ds.SeriesInstanceUID
# start processing
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

        # erode
        kernelCircle = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        imgErodeC = cv.erode(img, kernelCircle)
        # mask
        kernelMask = cv.getStructuringElement(cv.MORPH_RECT, (8, 8))
        imgErodeM = cv.erode(img, kernelMask)
        imgMask = cv.dilate(imgErodeM, kernelMask)
        ret, imgMaskBin = cv.threshold(imgMask, 30, 255, cv.THRESH_BINARY)

        circles = cv.HoughCircles(imgErodeC,
                                  cv.HOUGH_GRADIENT,
                                  2,
                                  40,
                                  param1=70,
                                  param2=95,
                                  minRadius=100,
                                  maxRadius=130)
        imgCopy = img.copy()
        px_arrCopy = px_arr.copy()

        # Inside circles
        if circles is not None:
            circles = np.uint16(np.around(circles))

            # Sometimes, I will many cycles in a image.
            # The way I choose is based on the y vale
            # I choose the topest of the center of circle.
            argmax = np.argmin(circles[0, :, 1])

            circle = circles[0, argmax]

            # create binary mask
            height = img.shape[0]
            width = img.shape[1]
            # Prepare a black canvas:
            canvas = np.zeros((height, width))

            # Draw the outer circle:
            color = (255, 255, 255)
            thickness = -1
            centerX = circle[0]
            centerY = circle[1]
            radius = circle[2]
            cv.circle(canvas, (centerX, centerY), radius, color, thickness)

            # Create a copy of the input and mask input:
            imgCopy[canvas == 0] = 0

            px_arrCopy[canvas == 0] = 0
        # mask with erode image
        px_arrCopy[imgMaskBin == 0] = 0
        imgCopy[imgMaskBin == 0] = 0

        if isCrop:
            # Crop the roi:
            x = centerX - int(IMAGE_SIZE / 2)
            y = centerY - int(IMAGE_SIZE / 2)
            h = int(2 * IMAGE_SIZE / 2)
            w = int(2 * IMAGE_SIZE / 2)
            # prevent from out of range
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if x + w > imgCopy.shape[1]:
                x = imgCopy.shape[1] - w
            if y + h > imgCopy.shape[0]:
                y = imgCopy.shape[0] - h
            assert x >= 0, "the crop size should be smaller than img size."
            assert y >= 0, "the crop size should be smaller than img size."
            # crop image
            targetImg = imgCopy[y:y + h, x:x + w]
            targetPx_arr = px_arrCopy[y:y + h, x:x + w]
        else:
            targetImg = imgCopy
            targetPx_arr = px_arrCopy

        if isTwice:
            targetImg = np.concatenate((targetImg, targetImg), 1)
            targetPx_arr = np.concatenate((targetPx_arr, targetPx_arr), 1)

        # output circle dicom file matched center for 3d
        ds.SeriesInstanceUID = file_SeriesInstanceUID
        ds.PixelData = targetPx_arr.tobytes()
        ds.Rows = targetPx_arr.shape[0]
        ds.Columns = targetPx_arr.shape[1]
        ds.save_as(Path(outDirname, filename))

        # show image
        if isDraw:
            #  write original image
            cv.imwrite(
                outDirname + filename.split('.')[0] + '_origin' + '.png', cimg)
            if circles is not None:
                # draw the outer circle
                cv.circle(cimg, (circle[0], circle[1]),
                          circle[2] - shrinkToCenter, (0, 0, 255), 2)
                # draw the center of the circle
                cv.circle(cimg, (circle[0], circle[1]), 2, (0, 0, 255), 3)
                # cv.imshow('Crop img', targetImg)

            # cv.imshow('detected circles', cimg)
            cv.imwrite(
                outDirname + filename.split('.')[0] + '_withCircle' + '.png',
                cimg)
            cv.imwrite(
                outDirname + filename.split('.')[0] + '_afterProcess' + '.png',
                targetImg)
            # cv.imshow('imgMask', imgMask)
            # cv.imshow('imgMaskBin', imgMaskBin)
            # cv.setMouseCallback('detected circles', show_brightness)
            # cv.waitKey(0)
            # cv.destroyAllWindows()
