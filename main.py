import cv2 as cv
import numpy as np
import utils

widthImg = 800
heightImg = 800

img = cv.imread('imageSample.jpeg')
img = cv.resize(img, (widthImg, heightImg))

imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
imgBlur = cv.GaussianBlur(img, (5, 5), 1)
imgCanny = cv.Canny(imgBlur, 50, 50)

imgArray = ([img, imgGray, imgBlur, imgCanny])

imgStack = utils.stackImages(imgArray, 0.5) #0.5 is the scale

cv.imshow('Image', imgStack)
cv.waitKey(0)