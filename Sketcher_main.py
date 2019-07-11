'''
Using Correlation Trackers in Dlib, you can track any object in a video stream without needing to train a custom object detector.
Check out the tutorial at: http://www.codesofinterest.com/2018/02/track-any-object-in-video-with-dlib.html
'''
import numpy as np
import cv2
import dlib
from Sketcher import Sketcher
from copy import deepcopy
import sys
import math

# this variable will hold the coordinates of the mouse click events.
mousePoints = []

# setup flag
def mouseEventHandler(event, x, y, flags, param):
    # references to the global mousePoints variable
    global mousePoints

    # if the left mouse button was clicked, record the starting coordinates.
    if event == cv2.EVENT_LBUTTONDOWN:
        mousePoints = [(x, y)]

    # when the left mouse button is released, record the ending coordinates.
    elif event == cv2.EVENT_LBUTTONUP:
        mousePoints.append((x, y))

# create the video capture.
video_capture = cv2.VideoCapture(0)

# initialize the correlation tracker.
tracker = dlib.correlation_tracker()

# this is the variable indicating whether to track the object or not.
tracked = False

cap = cv2.VideoCapture("video5.mp4")
ret, image = cap.read()
img_masked = image.copy()
mask = np.zeros(image.shape[:2], np.uint8)
point = []
sketcher=Sketcher('image', [img_masked, mask], lambda : ((255, 255, 255), 255), point)
cap.release()

# saving all points and find largest rectangle
while True:
    key = cv2.waitKey()
    if key == 32:
        print('processing')
        break
max_x = 0
max_y = 0
min_x = 9999
min_y = 9999
for pt in point:
    if max_x < pt[0] : max_x = pt[0]
    if max_y < pt[1] : max_y = pt[1]
    if min_x > pt[0] : min_x = pt[0]
    if min_y > pt[1] : min_y = pt[1]

print((max_x, max_y), (min_x, min_y))
mousePoints = []
mousePoints.append((min_x, min_y))
mousePoints.append((max_x, max_y))

prex = (mousePoints[1][0] + mousePoints[0][0])/2
prey = (mousePoints[1][1] + mousePoints[0][1])/2

prex2 = (mousePoints[1][0] - mousePoints[0][0])
prey2 = (mousePoints[1][1] - mousePoints[0][1])

cap = cv2.VideoCapture("video5.mp4")
while(cap.isOpened()):
    # start capturing the video stream.
    ret, frame = cap.read()
    if ret:
        image = frame

        

        # input polylines
        '''
        pts = np.array(point, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (255, 255, 255), 5)
        '''
        # if we have two sets of coordinates from the mouse event, draw a rectangle.
        if len(mousePoints) == 2:
            #cv2.rectangle(image, mousePoints[0], mousePoints[1], (0, 255, 0), 2)
            pts = np.array(point, np.int32)
            pts = pts.reshape((-1, 1, 2))
            poly = cv2.polylines(image, [pts], True, (255, 255, 255), 15)
            dlib_rect = dlib.rectangle(mousePoints[0][0], mousePoints[0][1], mousePoints[1][0], mousePoints[1][1])
    
        # tracking in progress, update the correlation tracker and get the object position.
        if tracked == True:
            tracker.update(image)
            track_rect = tracker.get_position()
            x  = int(track_rect.left())
            y  = int(track_rect.top())
            x1 = int(track_rect.right())
            y1 = int(track_rect.bottom())
            difx = (x1+x)/2 - prex
            dify = (y1+y)/2 - prey
            prex = (x1+x)/2
            prey = (y1+y)/2

            # tracking specific shape
            ratiox = (x1-x)/prex2
            ratioy = (y1-y)/prey2
            ratiox = round(math.sqrt(ratiox), 5)
            ratioy = round(math.sqrt(ratioy), 5)
            
            prex2 = (x1-x)
            prey2 = (y1-y)


            for pt in point:
                pt[0] += difx/2
                pt[1] += dify/2

            # resizing specific shape
            for pt2 in point:

                if pt2[0] > (x1+x)/2:
                    pt2[0] = ((x1+x)/2 + ((x1+x)/2-pt2[0])*ratiox)
                elif pt2[0] <= (x1+x)/2:
                    pt2[0] = ((x1+x)/2 - (pt2[0]-(x1+x)/2)*ratiox)
                

                if pt2[1] > (y1+y)/2: 
                    pt2[1] = ((y1+y)/2 + ((y1+y)/2-pt2[1])*ratioy)
                elif pt2[1] <= (y1+y)/2:
                    pt2[1] = ((y1+y)/2 - (pt2[1]-(y1+y)/2)*ratioy)
                    
                
            pts = np.array(point, np.int32)
            pts = pts.reshape((-1, 1, 2))
            poly = cv2.polylines(image, [pts], True, (255, 255, 255), 20)
            
            #cv2.rectangle(image, (x, y), (x1, y1), (0, 0, 255), 2)

        # show the current frame.
        cv2.imshow('video5', image)

    # capture the keyboard event in the OpenCV window.
    ch = 0xFF & cv2.waitKey(1)

    # press "r" to stop tracking and reset the points.
    if ch == ord("r"):
        mousePoints = []
        tracked = False

    # start tracking the currently selected object/area.
    if len(mousePoints) == 2:
        #tracker.start_track(image, dlib_rect)
        tracker.start_track(image, dlib_rect)
        tracked = True
        mousePoints = []

    # press "q" to quit the program.
    if ch == ord('q'):
        break

# cleanup.
cap.release()
cv2.destroyAllWindows()