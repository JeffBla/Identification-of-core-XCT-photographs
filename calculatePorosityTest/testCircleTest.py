import numpy as np
import cv2 as cv

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
        print(f"x: {x}, y: {y}, color: {img[y,x]}")


# for i in range(1, 5):
#     imgFile = f'./bh-3 DICOM-20230421T075124Z-001/drive-download-20230505T100000Z-001/B3-15 test{i}.tif'
#     img = cv.imread(imgFile, cv.IMREAD_GRAYSCALE)
#     assert img is not None, "file could not be read, check with os.path.exists()"
#     img = cv.medianBlur(img, 5)
#     cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
#     imgCanny = cv.Canny(img, 30, 150)
#     circles = cv.HoughCircles(imgCanny,
#                               cv.HOUGH_GRADIENT,
#                               1.5,
#                               20,
#                               param1=70,
#                               param2=70,
#                               minRadius=85,
#                               maxRadius=110)
#     if circles is not None or None:
#         # circles = np.uint16(np.around(circles))
#         # for index, i in enumerate(circles[0, :]):
#         #     # draw the outer circle
#         #     cv.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
#         #     # draw the center of the circle
#         #     cv.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
#         #     #calculate the percent of brightness
#         #     blackCnt = 0
#         #     pixelCnt = 0
#         #     for idx, j in np.ndenumerate(img):
#         #         # # in the img most of pixels are black so use BrightnessThrehold the filter first
#         #         # if (j < config['BrightnessThrehold']):
#         #         #     # check is inside the circle
#         #         #     if (checkInCircle(i[0], i[1], i[2], idx[0], idx[1])):
#         #         #         blackCnt += 1
#         #         # there is a trick that img[a,b] -> corresponse to x->b, y->a in picture
#         #         if (checkInCircle(i[0], i[1], i[2], idx[1], idx[0])):
#         #             pixelCnt += 1
#         #             if (j < config['BrightnessThrehold']):
#         #                 # check is inside the circle
#         #                 blackCnt += 1
#         #     cv.putText(cimg, f'{blackCnt / pixelCnt}', (0, 45 + 45 * index),
#         #                cv.FONT_HERSHEY_SIMPLEX, config['imgTextFontScale'],
#         #                config['imgTextColor'], config['imgTextThickness'],
#         #                cv.LINE_AA)

#         print(imgFile)
#         cv.imshow('origin', img)
#         cv.imshow('canny', imgCanny)
#         # cv.imshow('detected circles', cimg)
#         cv.setMouseCallback('origin', show_brightness)
#         cv.waitKey(0)
#         cv.destroyAllWindows()
#     else:
#         cv.imshow('origin', img)
#         cv.imshow('canny', imgCanny)
#         print("undo " + imgFile)

for i in range(1, 3):
    imgFile = f'./bh-3 DICOM-20230421T075124Z-001/IM-0001-0764.tif'
    img = cv.imread(imgFile, cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    img = cv.medianBlur(img, 5)
    cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    imgCanny = cv.Canny(img, 30, 150)
    circles = cv.HoughCircles(imgCanny,
                              cv.HOUGH_GRADIENT,
                              1.5,
                              20,
                              param1=70,
                              param2=70,
                              minRadius=85,
                              maxRadius=110)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for index, i in enumerate(circles[0, :]):
            # draw the outer circle
            cv.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
            #calculate the percent of brightness
            blackCnt = 0
            pixelCnt = 0
            for idx, j in np.ndenumerate(img):
                # # in the img most of pixels are black so use BrightnessThrehold the filter first
                # if (j < config['BrightnessThrehold']):
                #     # check is inside the circle
                #     if (checkInCircle(i[0], i[1], i[2], idx[0], idx[1])):
                #         blackCnt += 1
                # there is a trick that img[a,b] -> corresponse to x->b, y->a in picture
                if (checkInCircle(i[0], i[1], i[2], idx[1], idx[0])):
                    pixelCnt += 1
                    if (j < config['BrightnessThrehold']):
                        # check is inside the circle
                        blackCnt += 1
            cv.putText(cimg, f'{blackCnt / pixelCnt}', (0, 45 + 45 * index),
                       cv.FONT_HERSHEY_SIMPLEX, config['imgTextFontScale'],
                       config['imgTextColor'], config['imgTextThickness'],
                       cv.LINE_AA)

        print(imgFile)
        # cv.imshow('origin', img)
        # cv.imshow('canny', imgCanny)
        cv.imshow('detected circles', cimg)
        cv.setMouseCallback('detected circles', show_brightness)
        cv.waitKey(0)
        cv.destroyAllWindows()
    else:
        print("undo " + imgFile)
