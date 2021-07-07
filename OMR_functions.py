import cv2
import numpy as np

def stackImages(imgArray,scale):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

def rectContour(contour):
    rectCon = []
    for i in contour:
         area = cv2.contourArea(i)
         #print(area)
         if area > 50:
             peri = cv2.arcLength(i, True)
             approx = cv2.approxPolyDP(i, 0.02*peri, True)    #contains all the coordinates of contours
             #print(len(approx))
             if len(approx) == 4:
                 rectCon.append(i)
    rectCon = sorted(rectCon, key = cv2.contourArea, reverse = True)        #sorting the rectangle contours based on area          
    return rectCon

def getCorners(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02*peri, True)        #We could have used the function before to find the corner points but that time we first needed it to sort the rectangles based upon area to get the indexes of contours 
    return approx

def reorder(myPoints):
    myPoints = myPoints.reshape((4,2))
    myPointsnew = np.zeros((4,1,2), np.int32)
    
    add = myPoints.sum(1)               #on axis 1 along the points i.e. rows
    
    myPointsnew[0] = myPoints[np.argmin(add)]
    myPointsnew[3] = myPoints[np.argmax(add)]
    
    diff = np.diff(myPoints, axis = 1)
    
    myPointsnew[1] = myPoints[np.argmin(diff)]
    myPointsnew[2] = myPoints[np.argmax(diff)]
    
    return myPointsnew

def splitboxes(image):
    rows = np.vsplit(image, 10)
    boxes =[]
    for r in rows:
        cols = np.hsplit(r, 4)
        for box in cols:
            boxes.append(box)
    return boxes


    
    
    
    
    


