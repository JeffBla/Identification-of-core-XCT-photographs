import numpy as np
import cv2 as cv

from config import config

for i in range(30, 854):
    imgFile = f'/IMG-0002-{i:0>5d}.bmp'
    img = cv.imread(config['filePath'] + imgFile)
    assert img is not None, "file could not be read, check with os.path.exists()"
    imgCopy = img.copy()
    imgGray = cv.cvtColor(imgCopy, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(imgGray, 150, 255, 0)

    contours, _ = cv.findContours(thresh, cv.RETR_LIST, 1)
    if len(contours) != 0:
        for i in range(len(contours)):
            if len(contours[i]) >= 5:
                cv.drawContours(imgCopy, contours, -1, (0, 0, 255), 3)
                ellipse = cv.fitEllipse(contours[i])
                # cv.ellipse(imgCopy, ellipse, (0, 0, 255), 3)
            else:
                # optional to "delete" the small contours
                pass
                # cv.drawContours(imgCopy, contours, -1, (0, 255, 0), -1)

    cv.imshow("Ellipse", imgCopy)
    cv.waitKey(0)
    cv.destroyAllWindows()