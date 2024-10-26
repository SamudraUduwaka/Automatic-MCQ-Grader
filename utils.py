
############################################################################

###### Some Utility Functions, but not needed to final implementation ######

############################################################################


import cv2 as cv
import numpy as np

def stackImages(imgArray, scale, lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv.cvtColor(imgArray[x][y], cv.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv.cvtColor(imgArray[x], cv.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

def rectContour(contour):
    rectCon = []
    for i in contour:
        area = cv.contourArea(i)
        #print(area)
        if area>50:
            peri = cv.arcLength(i, True)
            approx = cv.approxPolyDP(i, 0.02*peri, True) #True - assuming to be closed shape
            #print("Corner points: ", len(approx))
            if len(approx) == 4:
                rectCon.append(i)
    #print(len(rectCon))
    rectCon = sorted(rectCon, key=cv.contourArea, reverse=True)
    return rectCon

def getCornerPoints(cont):
    peri = cv.arcLength(cont, True)
    approx = cv.approxPolyDP(cont, 0.02*peri, True)
    return approx

def reOrder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    add = myPoints.sum(1)  #Access no 1 will add
    #print(myPoints)
    #print(add)
    myPointsNew[0] = myPoints[np.argmin(add)] #First point should be min of addition
    myPointsNew[3] = myPoints[np.argmax(add)] #Last point should be max of addition
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)] #[w,0]
    myPointsNew[2] = myPoints[np.argmax(diff)] #[0,h]
    #print(diff)
    return myPointsNew