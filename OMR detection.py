import cv2
import numpy as np
import OMR_functions
import xlsxwriter

###################
wImage = 500
hImage = 500
questions = 10
choices = 4
###################

#Making and writing in an excel file
workbook = xlsxwriter.Workbook('hello.xlsx')
worksheet = workbook.add_worksheet()
Grading = []

wc = cv2.VideoCapture(0)
wc.open(0)
wc.set(3,640)       #width
wc.set(4,480)       #height
wc.set(10,500)

while(wc.isOpened()):

    ret, img = wc.read()
    if ret == True:
        img = cv2.resize(img, (600, 500))
        
        
        #imgCropped = img[0:500, 20:600]
        #cv2.imshow('Cropped Image', imgCropped)                    #cropped image
        #cv2.waitKey(0)
        
        
        img_Contours = img.copy()
        img_biggest = img.copy()
        
        
        ###IMAGE PREPROCESSING
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
        imgCanny = cv2.Canny(imgBlur, 10, 50)
        
        
        ###Finding all contours
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)    #We do not need any approximations
        cv2.drawContours(img_Contours, contours, -1, (0, 255, 0), 5)              #-1 is the index of contours
        imgblank = np.zeros_like(img)     #to create a blank image of same size as of input image
        
        #finding rectangle
        rect_contours = OMR_functions.rectContour(contours)
        biggest = OMR_functions.getCorners(rect_contours[0])              #largest rectangle
        grade = OMR_functions.getCorners(rect_contours[1])                #second largest rectangle here needed the most
        
        biggest = OMR_functions.reorder(biggest)
        grade = OMR_functions.reorder(grade)
        centre = ((grade[0][0][0] + grade[1][0][0] + grade[2][0][0] + grade[3][0][0])//4, (grade[0][0][1] + grade[1][0][1] + grade[2][0][1] + grade[3][0][1])//4)
        
        if biggest.size!= 0 and grade.size!=0 :
            cv2.drawContours(img_biggest, biggest, -1, (0, 255, 0), 20)    
            cv2.drawContours(img_biggest, grade, -1, (255, 0, 0), 20)    
            
            #warping the omr
            pt1 = np.float32(biggest)
            pt2 = np.float32([[0, 0], [wImage, 0], [0, hImage], [wImage, hImage]])
            matrix = cv2.getPerspectiveTransform(pt1, pt2)
            imgWarpColored = cv2.warpPerspective(img, matrix, (wImage, hImage)) 
            
            #warping the gradepoints
            pt1_G = np.float32(grade)
            pt2_G = np.float32([[0, 0], [wImage, 0], [0, hImage], [wImage, hImage]])
            matrix_G = cv2.getPerspectiveTransform(pt1_G, pt2_G)
            imgWarpColored_G = cv2.warpPerspective(img, matrix_G, (wImage, hImage)) 
            
            #Applying the threshhold, the circles which are filled have more color pixels, so we use this logic to find the same
            imgWarpGrey = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
            imgThresh = cv2.threshold(imgWarpGrey, 150, 255, cv2.THRESH_BINARY_INV)[1]  #It is a tuple so in order to get the required one we have put [1]
            boxes = OMR_functions.splitboxes(imgThresh)        # contains all the boxes of each choice
            #cv2.imshow('123', boxes[2])
            
            my_sheet = np.zeros((questions, choices))
            count_row = 0
            count_col = 0
            
            for image in boxes:
               Pixels = cv2.countNonZero(image)                        #getting all the pixels and storing it in a similar kind of array
               my_sheet[count_row][count_col] = Pixels
               count_col +=1
               if count_col == choices : 
                   count_row += 1
                   count_col = 0
            
            for i in range(questions):                              #replacing all the high pixel values with 1 and rest 0
                 ans = max(my_sheet[i])
                 for j in range(choices) :
                     if my_sheet[i][j] == ans : 
                         my_sheet[i][j] = 1
                     else :
                         my_sheet[i][j] = 0
            print(my_sheet)
                
            Answer_sheet = [[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 0],
                            [1, 0, 0, 0],
                            [1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1],
                            [1, 0, 0, 0],
                            [0, 0, 0, 1]]
            
            score = 0 
            
            #Checking the answersheet
            for i in range(questions): 
                for j in range(choices) :
                    if my_sheet[i][j] == 1 and Answer_sheet[i][j] == 1:
                        score += 1
            Result = float((score*100)/questions)
            #print('Result : ', str(Result) + ' %')
            cv2.putText(img, str(Result) + ' %' , centre, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 150, 0), 3)
            cv2.imshow('OMR', img)
            
            if cv2.waitKey(1) & 0xFF == ord('s'):
                Grading.append(scores)
  
            # Break the loop
            else: 
                break
            
        
        
        
        
        #stacking all the images
        #imgArray = ([img, imgGray, imgBlur, imgCanny], [img_Contours, img_biggest, imgWarpColored, imgThresh])
        #imgStacked = OMR_functions.stackImages(imgArray, 0.5)
        
        
        
       
row = 0
column = 0
    
# iterating through content list 
for item in Grading : 
    
    # write operation perform 
    worksheet.write(row, column, item) 
    # incrementing the value of row by one 
    # with each iteratons. 
    row += 1
      
workbook.close() 
wc.release()
cv2.destroyAllWindows()










