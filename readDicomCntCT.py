from pydicom import dcmread
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from config import config


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


# with open(config['filePathOrigin'] + '/23966887', 'rb') as f:
#     ds = dcmread(f)
#     with open('dsInfo.txt', 'w') as tf:
#         tf.write(str(ds))
#     # print(ds.PhotometricInterpretation)
#     # arr = ds.pixel_array
#     # arr[arr > 100] = 300
#     # ds.PixelData = arr.tobytes()
#     # print(ds.pixel_array)
#     # print(ds.PhotometricInterpretation)
#     plt.imshow(ds.pixel_array)
#     plt.show()

with open('./bh-3 DICOM-20230421T075124Z-001/IM-0001-0001.dcm', 'rb') as f:
    ds = dcmread(f)
    print("正常的或被压缩的：" + ds.file_meta.TransferSyntaxUID.name)
    print(f"Rescale Slope: {ds.RescaleSlope}")
    print(f"Rescale Intercept: {ds.RescaleIntercept}")
    print("The formula of CT value: Hu = pixel * slope + intercept")
    with open('dsInfo.txt', 'w') as tf:
        tf.write(str(ds))

    # 提取像素數據
    px_arr = np.array(ds.pixel_array)
    # CT value
    Hu = px_arr * ds.RescaleSlope + ds.RescaleIntercept
    CTG = np.max(px_arr)
    afterW_Hu = (CTG - Hu) / CTG
    # # rescale original 16 bit image to 8 bit values [0,255]
    x0 = np.min(px_arr)
    x1 = np.max(px_arr)
    y0 = 0
    y1 = 255.0
    i8 = ((px_arr - x0) * ((y1 - y0) / (x1 - x0))) + y0

    # # create new array with rescaled values and unsigned 8 bit data type
    o8 = i8.astype(np.uint8)

    print(f"rescaled data type={o8.dtype}")

    # do the Hough transform
    img = cv.medianBlur(o8, 5)
    cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    imgCanny = cv.Canny(img, 30, 150)
    circles = cv.HoughCircles(imgCanny,
                              cv.HOUGH_GRADIENT,
                              1.5,
                              20,
                              param1=70,
                              param2=70,
                              minRadius=85,
                              maxRadius=95)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for index, i in enumerate(circles[0, :]):
            # draw the outer circle
            cv.circle(cimg, (i[0], i[1]), i[2] - 2, (0, 0, 255), 2)
            # draw the center of the circle
            cv.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)

            blackCnt = 0
            pixelCnt = 0
            for idx, j in np.ndenumerate(Hu):
                if (checkInCircle(i[0], i[1], i[2] - 2, idx[1], idx[0])):
                    pixelCnt += 1
                    # CT < 0 is for fiuld
                    if (j < 0):
                        # check is inside the circle
                        blackCnt += 1
            cv.putText(cimg, f'{blackCnt / pixelCnt}', (0, 45 + 45 * index),
                       cv.FONT_HERSHEY_SIMPLEX, config['imgTextFontScale'],
                       config['imgTextColor'], config['imgTextThickness'],
                       cv.LINE_AA)

    cv.imshow('detected circles', cimg)
    cv.setMouseCallback('detected circles', show_brightness)
    cv.waitKey(0)
    cv.destroyAllWindows()