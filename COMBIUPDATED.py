import cv2
import numpy as np
from matplotlib import pyplot as plt
import operator
import os
import sqlite3
import time
import datetime
import random
from dateutil.parser import parse
from datetime import datetime
import time
import serial
import difflib    

import RPi.GPIO as GPIO
ser = serial.Serial('/dev/ttyACM0', 9600)


##test camera for entry##

def test_camera0():

    
    cam = cv2.VideoCapture(1)

    cv2.namedWindow("test")

    img_counter = 0

    while True:
        ret, frame = cam.read()
        cv2.imshow("test", frame)
        cv2.imshow("crop",frame[298:420,42:546])
        if not ret:
            break
        k = cv2.waitKey(1)

        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "sample.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()
    cv2.destroyAllWindows()


################################################################################



##test camera for exit##

def test_camera1():


    cam = cv2.VideoCapture(0)

    cv2.namedWindow("test")

    img_counter = 0

    while True:
        ret, frame = cam.read()
        cv2.imshow("test", frame)
        cv2.imshow("crop",frame[298:420,42:546])
        if not ret:
            break
        k = cv2.waitKey(1)

        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "sample.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()
    cv2.destroyAllWindows()

    
###########################################################################

## ROI

def roi():
    image=cv2.imread("sample.png",0)
    new=image[298:420,42:546]
    #image[478:600,200:700]=new
    L1 = cv2.Canny(new, 50, 300, L2gradient=False)
    L2 = cv2.Canny(new, 300, 300, L2gradient=True)
    edges = cv2.Canny(new,100,200)
    ret, o5 = cv2.threshold(new, 10, 255, cv2.THRESH_OTSU)
    cv2.imwrite('roi1.png',o5)
   
    list1=[ ]
    img = cv2.imread('roi1.png')
    cv2.imshow("original", img)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('gray_image.png',gray_image)

    cv2.imshow('gray_image',gray_image)

    ret,thresh=cv2.threshold(gray_image,175,255,cv2.THRESH_BINARY)
    _,contours,_=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for i in range (len(contours)):
        perimeter=cv2.arcLength(contours[i],True)
        if perimeter >500 and perimeter  <5000:
            cv2.drawContours(img,contours,i,(0,255,0),2)
            r=cv2.boundingRect(contours[i])
            cv2.imwrite('roi.png',img[r[1]:r[1]+r[3],r[0]:r[0]+r[2]])
            list1.append(i)
        

    cv2.imshow("threshold", thresh)
    cv2.imshow("region of intrest",img)
    #r = cv2.boundingRect(i)
    cv2.imwrite('region of intrest.png',img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]])

        
#############################################################################


## Train & Test

def char_recog():

    # module level variables ##########################################################################
    MIN_CONTOUR_AREA = 70
    RESIZED_IMAGE_WIDTH = 20
    RESIZED_IMAGE_HEIGHT = 30
    a=300.0

    ###################################################################################################
    class ContourWithData():

        # member variables ############################################################################
        npaContour = None           # contour
        boundingRect = None         # bounding rect for contour
        intRectX = 0                # bounding rect top left corner x location
        intRectY = 0                # bounding rect top left corner y location
        intRectWidth = 0            # bounding rect width
        intRectHeight = 0           # bounding rect height
        fltArea = 0.0               # area of contour

        def calculateRectTopLeftPointAndWidthAndHeight(self):               # calculate bounding rect info
            [intX, intY, intWidth, intHeight] = self.boundingRect
            self.intRectX = intX
            self.intRectY = intY
            self.intRectWidth = intWidth
            self.intRectHeight = intHeight

        def checkIfContourIsValid(self):                            # this is oversimplified, for a production grade program
            if ((self.fltArea < MIN_CONTOUR_AREA) or (self.fltArea > a)):
            
                return False        # much better validity checking would be necessary
            else:
                print(self.fltArea)
                return True
            
    ###################################################################################################
    def main1():
        allContoursWithData = []                # declare empty lists,
        validContoursWithData = []              # we will fill these shortly

        try:
            npaClassifications = np.loadtxt("classifications.txt", np.float32)                  # read in training classifications
        except:
            print ("error, unable to open classifications.txt, exiting program\n")
            os.system("pause")
            return
        # end try

        try:
            npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)                 # read in training images
        except:
            print ("error, unable to open flattened_images.txt, exiting program\n")
            os.system("pause")
            return
        # end try

        npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train

        kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object

        kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

        imgTestingNumbers = cv2.imread("region of intrest.png")          # read in testing numbers image

        if imgTestingNumbers is None:                           # if image was not read successfully
            print ("error: image not read from file \n\n")        # print error message to std out
            os.system("pause")                                  # pause so user can see error message
            return                                              # and exit function (which exits program)
        # end if

        imgGray = cv2.cvtColor(imgTestingNumbers, cv2.COLOR_BGR2GRAY)       # get grayscale image
        imgBlurred = cv2.GaussianBlur(imgGray, (3,3), 0)                    # blur

                                                            # filter image from grayscale to black and white
        imgThresh = cv2.adaptiveThreshold(imgBlurred,                           # input image
                                          255,                                  # make pixels that pass the threshold full white
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # use gaussian rather than mean, seems to give better results
                                          cv2.THRESH_BINARY_INV,                # invert so foreground will be white, background will be black
                                          11,                                   # size of a pixel neighborhood used to calculate threshold value
                                          2)                                    # constant subtracted from the mean or weighted mean

        imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image

        imgContours, npaContours, npaHierarchy = cv2.findContours(imgThreshCopy,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                     cv2.RETR_EXTERNAL,         # retrieve the outermost contours only
                                                     cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points

        for npaContour in npaContours:                             # for each contour
            contourWithData = ContourWithData()                                             # instantiate a contour with data object
            contourWithData.npaContour = npaContour                                         # assign contour to contour with data
            contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
            contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                    # get bounding rect info
            contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
            allContoursWithData.append(contourWithData)                                     # add contour with data object to list of all contours with data
        # end for

        for contourWithData in allContoursWithData:                 # for all contours
            if contourWithData.checkIfContourIsValid():             # check if valid
                validContoursWithData.append(contourWithData)       # if so, append to valid contour list
            # end if
        # end for

        validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right

        strFinalString = ""         # declare final string, this will have the final number sequence by the end of the program

        for contourWithData in validContoursWithData:            # for each contour
                                                    # draw a green rect around the current char
            cv2.rectangle(imgTestingNumbers,                                        # draw rectangle on original testing image
                          (contourWithData.intRectX, contourWithData.intRectY),     # upper left corner
                          (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),      # lower right corner
                          (0, 255, 0),              # green
                          2)                        # thickness

            imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,     # crop char out of threshold image
                               contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage

            npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

            npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

            retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest

            strCurrentChar = str(chr(int(npaResults[0][0])))                                             # get character from results

            if strCurrentChar==" ":
               continue
            else:
               strFinalString = strFinalString + strCurrentChar# append current char to full string


         # end for

        print ("\n" + strFinalString + "\n")                  # show the full string

        cv2.imshow("imgTestingNumbers", imgTestingNumbers)# show input image with green boxes drawn around found digits
        os.remove("file.txt")
        file=open('file.txt','a')
        file.write(strFinalString)
        file.close()
        cv2.waitKey(5000)                                          # wait for user key press
        cv2.destroyAllWindows()             # remove windows from memory
        

    ###################################################################################################
    #if __name__ == "__main__":
    main1()
    #end if 

###############################################################################################################################################



## Entry database

    
def data_entry():
   
    import sqlite3
    import time
    import datetime
    #from TrainAndTest import strFinalString
    import random
    print('entry')
    conn = sqlite3.connect('tutorial.db')
    c = conn.cursor()

    def create_table():
        c.execute("CREATE TABLE IF NOT EXISTS parking(unix REAL, datestamp TEXT)")

    create_table()




    def dynamic_data_entry():
        f = open("file.txt", "r")
        a=f.read() 
        unix = int(time.time())
        date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        #timmy = str(time.time.fromtimestamp(date).strftime('%H:%M:%S'))
        

        c.execute("INSERT INTO parking (unix, datestamp) VALUES (?, ?)",
              (date,a))
        
        
        conn.commit()



        
    for i in range(0):
        dynamic_data_entry()
      
    
    c.close
    conn.close()

####################################################################################################################


    
## Exit database


def data_exit():
    import sqlite3
    import time
    from datetime import datetime
    import datetime
    from dateutil.parser import parse
    import random


    n=0
    db = sqlite3.connect('tutorial.db')
    cursor = db.cursor()
    cursor.execute('select *from parking' )
    #g=strFinalString
    f = open("file.txt", "r")
    g=f.read() 
    for row in cursor:


        text_1 = g    #strings to be compared 

        text_2 = row[2]    # pass the values dynamically here


        sequence = difflib.SequenceMatcher(isjunk=None,a=text_1,b=text_2)   # takes 3 arguments 

        difference = sequence.ratio()*100              # fraction to decimal conversion   #ratio function..

        difference = round(difference,2)   #reduces the number of decimel places.

        print( str(difference) + "%match" )


        if difference>= 65 :
           n=n+1
           print('This is it')
           print (n)  
           unix = int(time.time())
           date1 = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
           print(date1)
           #n=n+1
           db = sqlite3.connect('tutorial.db')
           t1=""
           t2=""
           t1 = str(row[1])
           t2 = str(date1)
           l1 = t1.split()
           l2 = t2.split()
           print(l1)
           print(l2)
           s1 = ""
           s2 = ""
           for i in l1:
             if i not in l2:
                s1 = s1 + " " + i 
           for j in l2:
             if j not in l1:
                s2 = s2 + " " + j 

           new = s1 + "," +s2
           print (new)
           b,c= new.split(",")
           print(b)
           print(c)
           FMT=' %H:%M:%S'
           tdelta=datetime.datetime.strptime(c,FMT) - datetime.datetime.strptime(b,FMT)
           print(tdelta)
           q=(str(tdelta)[:1])
           print(int(q))
           if ((int(q))==0):
             print('10 rupees')
           else:
             print((int(q))*20)  
             print('rupees')
           db.close()
           cursor.close()
           
           db = sqlite3.connect('tutorial.db')
           cursor = db.cursor()
           unix=g
           

           cursor.execute("UPDATE parking SET unix = ? WHERE num = ?", ('   ', n))
           cursor.execute("UPDATE parking SET datestamp = ? WHERE num = ?", ('   ', n))
           db.commit()       
           cursor = db.cursor()
           break
        else:  
           n=n+1
           print('not found')
          
         #print('{0}:{1}'.format(row[0],row[1]))
     

#################################################################################################################################################


           
## Led strip

def led():
    import sqlite3
    import time
    from datetime import datetime
    import datetime
    from dateutil.parser import parse
    import random
    import RPi.GPIO as GPIO

    
  


    n=0
    db = sqlite3.connect('tutorial.db')
    c = db.cursor()
    print(c)
    c.execute('select *from parking' )
    f = open("file.txt", "r")
    a=f.read() 
    unix = int(time.time())
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
    num= int(time.time())

    for row in c:
        n=n+1
        if row[2]=='   ':
            if n<=5:
                print(n)
                print("LEDS TO SECTION A")
                ser.write(str.encode('l'))
                ser.flushOutput()
                time.sleep(1)
                c.execute('''UPDATE parking SET unix =?,datestamp =? WHERE num=?''',(date,a,n))
                db.commit()
                break
            else:
                print("LEDS TO SECTION B")
                ser.write(str.encode('r'))
                ser.flushOutput()
                time.sleep(1)
                c.execute('''UPDATE parking SET unix =?,datestamp =? WHERE num=?''',(date,a,n))
                db.commit()
                break
        else:
            print("NO VACANT SLOTS")
            
            
#####################################################################################################################################################


## Servo_entry

def servo_entry():

    ser.write(str.encode('1')) #send 1
    print ("servo turned ON at entrance ")
    time.sleep(1)

    
#############################################################################################################################################


## Servo_exit

def servo_exit():
     ser.write(str.encode('0') )#send 1
     print ("servo turned ON at exit ")
     time.sleep(1)
    


##########################################################################################################################

## Entry IR

def entry_ir():

   

    
    try: 
       while True:
          val= ser.readline().decode("ascii")
          val=int(val)
          
          if (val==0):
              print ("Car Detected at entry")
              test_camera0()
              roi()
              char_recog()
              #data_entry()
              servo_entry()
              led()
              ser.flushInput()
              break
             
              while (val==0):
                  time.sleep(0.2)
          else:
              break       
          
                  

    except KeyboardInterrupt:
        GPIO.cleanup()


#############################################################################################################################################

## Exit IR

def exit_ir():



    try: 
       while True:
          val= ser.readline().decode("ascii")
          val=int(val)
          
          if (val==1):
              print ("Car Detected at exit")
              test_camera1()
              roi()
              char_recog()
              
              data_exit()
              servo_exit()
              ser.flushInput()
              break
              
              while (val==1):
                  time.sleep(0.2)
          else:
              break
                  
      
                  

    except KeyboardInterrupt:
        GPIO.cleanup()

############################################################################################################################


## Main function


def main():

   
    ##Entry part
    #print("entry")
    entry_ir()

    
    ##Exit part
    #print("exit")
    exit_ir()

    main()
   
main()

