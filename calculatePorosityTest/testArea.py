import numpy as np
import cv2 as cv

from config import config

for i in range(1, 835):
    imgFile = f'/IMG-0002-{i:0>5d}.bmp'
    img = cv.imread(config['filePath'] + imgFile)
    imgCopy = img.copy()
    imgGray = cv.cvtColor(imgCopy, cv.COLOR_BGR2GRAY)
    assert img is not None, "file could not be read, check with os.path.exists()"
    ret, thresh = cv.threshold(imgGray, 127, 255, 0)
    contours, hierarchy = cv.findContours(thresh, 2, 1)

    cnt = contours
    big_contour = []
    max = 0
    for i in cnt:
        area = cv.contourArea(i)  #--- find the contour having biggest area ---
        if (area > max):
            max = area
            big_contour = i

    final = cv.drawContours(imgCopy, big_contour, -1, (0, 255, 0), 3)

    print(imgFile)
    cv.imshow('final', final)
    cv.waitKey(0)
    cv.destroyAllWindows()
