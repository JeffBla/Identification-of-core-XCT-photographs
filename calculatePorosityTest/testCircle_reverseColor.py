import numpy as np
import cv2 as cv

from config import config


# roughParam default is 5
def checkRoughInCircle(cx, cy, r, idxX, idxY, roughParam=10) -> bool:
    if (idxX - cx)**2 + (idxY - cy)**2 < (r - roughParam)**2:
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
    imgBlur = cv.medianBlur(img, 5)
    cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    imgCanny = cv.Canny(imgBlur, 30, 150)
    circles = cv.HoughCircles(imgCanny,
                              cv.HOUGH_GRADIENT,
                              1.5,
                              20,
                              param1=70,
                              param2=70,
                              minRadius=85,
                              maxRadius=110)
    # on;y when having one cicle can output
    if circles is not None and len(circles[0, :]) == 1:
        for index, i in enumerate(circles[0, :]):
            # reverse color
            for idx, j in np.ndenumerate(img):
                # there is a trick that img[a,b] -> corresponse to x->b, y->a in picture
                if (checkRoughInCircle(i[0], i[1], i[2], idx[1], idx[0])):
                    # check is inside the circle
                    if (j < config['crackBrightnessThrehold']):
                        # black to white
                        img[idx[0], idx[1]] = 255
                    else:
                        #white to black
                        img[idx[0], idx[1]] = 0
                else:
                    img[idx[0], idx[1]] = 0

        print(imgFile)
        cv.imwrite(config['filePathReverseOut'] + imgFile, img)
        cv.waitKey(0)
        cv.destroyAllWindows()
    else:
        print("undo " + imgFile)
