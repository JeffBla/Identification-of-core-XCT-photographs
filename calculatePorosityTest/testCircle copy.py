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


for i in range(1, 854):
    imgFile = f'/IMG-0002-{i:0>5d}.bmp'
    img = cv.imread(config['filePath'] + imgFile, cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    img = cv.medianBlur(img, 5)
    cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    circles = cv.HoughCircles(img,
                              cv.HOUGH_GRADIENT_ALT,
                              1.5,
                              20,
                              param1=500,
                              param2=0.9,
                              minRadius=70,
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
        cv.imshow('test', img)
        cv.imshow('detected circles', cimg)
        cv.setMouseCallback('detected circles', show_brightness)
        cv.waitKey(0)
        cv.destroyAllWindows()
    else:
        print("undo " + imgFile)
