import cv2 as cv
import numpy as np
import utils

widthImg = 800
heightImg = 800

img = cv.imread('imageSample.jpeg')
img = cv.resize(img, (widthImg, heightImg))
imgContours = img.copy()
imgBiggestContours = img.copy()

imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
imgBlur = cv.GaussianBlur(img, (5, 5), 1)
imgCanny = cv.Canny(imgBlur, 50, 50)

#Finding all contours
contours, hierarchy = cv.findContours(imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
cv.drawContours(imgContours, contours, -1, (0, 255, 0), 10)

#Find rectangles
rectCon = utils.rectContour(contours)
biggestContour = utils.getCornerPoints(rectCon[0])
#print(biggestContour.shape)
#gradePoints = utils.getCornerPoints(rectCon[1])  if a grader box is present
#print(biggestContour)

if biggestContour.size != 0 : #and gradePoints.size != 0
    cv.drawContours(imgBiggestContours, biggestContour, -1, (0, 255, 0), 20)
    #cv.drawContours(imgBiggestContours, gradePoints, -1, (255, 0, 0), 20)

    utils.reOrder(biggestContour)

imgBlank = np.zeros_like(img)

imgArray = ([img, imgGray, imgBlur, imgCanny],
            [imgContours, imgBiggestContours, imgBlank, imgBlank])

imgStack = utils.stackImages(imgArray, 0.5) #0.5 is the scale

cv.imshow('Image', imgStack)
cv.waitKey(0)