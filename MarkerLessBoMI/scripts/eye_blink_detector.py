"""
This script using Google Mediapipe is able to track
eyes landmark, on the image frame acquired by the webcam and processed using OpenCV.
Two lines, one vertical and the second one horizontal,  are selected using eyes indices.
In order to understand if the eyes is closed, the ratio between these two lines is calculated.
If this ratio is grater than CLS_RATIO_TRESHOLD constant, the eyes are considered closed.
"""

import cv2 as cv
import mediapipe as mp
import time , math,os,threading
from scripts import utils 
import numpy as np
from scripts.stopwatch import StopWatch
from main_reaching import manage_fsm_state

#open eyes_cls_calib
path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\calib\\eyes_cls_calib.txt"
calib_eyes_file = open(path,"w+")

# variables 
frame_counter = 0
CEF_COUNTER = 0
CEF_WINK_COUNTER = 0
TOTAL_BLINKS = 0
TOTAL_EYES_CLS = 0
TOTAL_WINK = 0
cls_eyes_flag = False
rv_eye = []
lv_eye = []
lx_eye_threshold = None
rx_eye_threshold = None

# constants
CLOSED_EYES_FRAME =3
FONTS =cv.FONT_HERSHEY_COMPLEX

#closed threshold
CLS_RATIO_THRESHOLD = 4
CLS_TIME_THRESHOLD = 1500 #ms

# face bounder indices 
FACE_OVAL=[ 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,67, 109]

# lips indices for Landmarks
LIPS=[ 61, 146, 91, 181, 84, 17, 314, 405, 321, 375,291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95,185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78 ]
LOWER_LIPS =[61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
UPPER_LIPS=[ 185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78] 
# Left eyes indices 
LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
LEFT_EYEBROW =[ 336, 296, 334, 293, 300, 276, 283, 282, 295, 285 ]

# right eyes indices
RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]  
RIGHT_EYEBROW=[ 70, 63, 105, 66, 107, 55, 65, 52, 53, 46 ]

map_face_mesh = mp.solutions.face_mesh
# camera object 
camera = cv.VideoCapture(0)

class Eye_Detector():
    """
    Class that group all the functionalities for eye blinkink detector for manage the FSM
    """
    def __init__(self):
        self.cls_eyes = False
        self.three_times_cls = False
        self.wink = False


#Eye Detector Obj
eye_detector_fsm = Eye_Detector()

# landmark detection function 
def landmarksDetection(img, results, draw=False):
    img_height, img_width= img.shape[:2]
    # list[(x,y), (x,y)....]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw :
        [cv.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    # returning the list of tuples for each landmarks 
    return mesh_coord

# Euclaidean distance 
def euclaideanDistance(point, point1):
    x, y = point
    x1, y1 = point1
    distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
    return distance

# Blinking Ratio
def blinkRatio(img, landmarks, right_indices, left_indices):
    # Right eyes 
    # horizontal line 
    rh_right = landmarks[right_indices[0]]
    rh_left = landmarks[right_indices[8]]
    # vertical line 
    rv_top = landmarks[right_indices[12]]
    rv_bottom = landmarks[right_indices[4]]
    # draw lines on right eyes 
    # cv.line(img, rh_right, rh_left, utils.GREEN, 2)
    # cv.line(img, rv_top, rv_bottom, utils.WHITE, 2)

    # LEFT_EYE 
    # horizontal line 
    lh_right = landmarks[left_indices[0]]
    lh_left = landmarks[left_indices[8]]

    # vertical line 
    lv_top = landmarks[left_indices[12]]
    lv_bottom = landmarks[left_indices[4]]

    rhDistance = euclaideanDistance(rh_right, rh_left)
    rvDistance = euclaideanDistance(rv_top, rv_bottom)

    lvDistance = euclaideanDistance(lv_top, lv_bottom)
    lhDistance = euclaideanDistance(lh_right, lh_left)

    reRatio = rhDistance/rvDistance
    leRatio = lhDistance/lvDistance

    ratio = (reRatio+leRatio)/2
    return ratio, lvDistance, rvDistance


def init_blinking_detection(start,lx_threshold,rx_threshold,cap):
    global lx_eye_threshold, rx_eye_threshold
    lx_eye_threshold = lx_threshold
    rx_eye_threshold = rx_threshold
    if start:
        print("Blinking Eyes Detection Thread is starting")
        blinking_thread = threading.Thread(target=blinking_detection,args=(start,cap))
        blinking_thread.start()

def blinking_detection(start,cap):

    global frame_counter, lx_eye_threshold, rx_eye_threshold, map_face_mesh
    global CEF_COUNTER, CEF_WINK_COUNTER, TOTAL_BLINKS, TOTAL_EYES_CLS, TOTAL_WINK, cls_eyes_flag, CLOSED_EYES_FRAME, FONTS,CLS_RATIO_THRESHOLD, LEFT_EYE, RIGHT_EYE
    global eye_detector_fsm
   

    # camera object 
    # camera = cv.VideoCapture(0)

    #stopwatches for counting the eyes closure 
    timer_cls_eyes = StopWatch() 
    timer_cls_three_times = StopWatch()
    timer_wink = StopWatch()
    
    #counters 
    eye_cls_counter = 0  
    three_time_counter = 0 
    first_time_flag = True

    #flags
    winking_flag = False

    #eyes closed threshold
    EYE_CLS_THRESHOLD = 3

    #eye winking time threshold 
    WINK_TIME_THRESHOLD = 250 #ms

    with map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:
 
        
        # starting time here 
        start_time = time.time()
        # starting Video loop here.
        while True:
            frame_counter +=1 # frame counter
            ret, frame = cap.read() # getting frame from camera 
            if not ret: 
                break # no more frames break
            #  resizing frame
            
            frame = cv.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)
            frame_height, frame_width= frame.shape[:2]
            rgb_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
            results  = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                mesh_coords = landmarksDetection(frame, results, False)
                ratio,lvDistance,rvDistance = blinkRatio(frame, mesh_coords, RIGHT_EYE, LEFT_EYE)

                #Both eyes closed
                if (lvDistance <= lx_eye_threshold) and (rvDistance <= rx_eye_threshold):
                    if cls_eyes_flag == False:
                        timer_cls_eyes.start()
                        cls_eyes_flag = True
                        if first_time_flag:
                            timer_cls_three_times.start()
                            first_time_flag = False
                    if (timer_cls_three_times.elapsed_time > 1000):
                        timer_cls_three_times.start()
                        eye_cls_counter = 0
                        first_time_flag = True

                    CEF_COUNTER +=1
                    # cv.putText(frame, 'Blink', (200, 50), FONTS, 1.3, utils.PINK, 2)
                    utils.colorBackgroundText(frame,  f'Blink', FONTS, 1.7, (int(frame_height/2), 100), 2, utils.YELLOW, pad_x=6, pad_y=6, )

                else:
                    timer_cls_eyes.start()
                    cls_eyes_flag = False
                    already_closed = False
                    if CEF_COUNTER>CLOSED_EYES_FRAME:
                        TOTAL_BLINKS +=1
                        CEF_COUNTER =0
                        eye_cls_counter +=1
               
                #winking
                if (lvDistance <= lx_eye_threshold) ^ (rvDistance <= rx_eye_threshold):
                    if winking_flag == False:
                        timer_wink.start()
                        winking_flag = True
                    
                    CEF_WINK_COUNTER +=1
                    utils.colorBackgroundText(frame,  f'Wink', FONTS, 1.7, (int(frame_height/2), 100), 2, utils.YELLOW, pad_x=6, pad_y=6, )
                else:
                    timer_wink.start()
                    winking_flag = False
                    already_wink = False
                    if CEF_WINK_COUNTER >CLOSED_EYES_FRAME:
                        CEF_WINK_COUNTER = 0

                
                # if statement to detect three closure in 1 seconds
                if eye_cls_counter >= EYE_CLS_THRESHOLD:
                    timer_cls_three_times.start()
                    three_time_counter += 1 
                    first_time_flag = True
                    eye_cls_counter = 0
                    eye_detector_fsm.three_times_cls = True
                    manage_fsm_state(eye_detector_fsm)
                    eye_detector_fsm.three_times_cls = False

                # if statement to detect eyes closure for 1 second
                if (timer_cls_eyes.elapsed_time >= CLS_TIME_THRESHOLD) and (not already_closed):
                    TOTAL_EYES_CLS +=1
                    timer_cls_eyes.start()
                    already_closed = True
                    eye_detector_fsm.cls_eyes = True
                    manage_fsm_state(eye_detector_fsm)
                    eye_detector_fsm.cls_eyes = False

                # if statement to detect eye wink
                if (timer_wink.elapsed_time >=  WINK_TIME_THRESHOLD) and (not already_wink):
                    TOTAL_WINK +=1
                    timer_wink.start()
                    already_wink = True
                    eye_detector_fsm.wink = True
                    manage_fsm_state(eye_detector_fsm)
                    eye_detector_fsm.wink = False

                # cv.putText(frame, f'Total Blinks: {TOTAL_BLINKS}', (100, 150), FONTS, 0.6, utils.GREEN, 2)
                utils.colorBackgroundText(frame,  f'Total Blinks: {TOTAL_BLINKS}', FONTS, 0.7, (30,150),2)
                utils.colorBackgroundText(frame,  f'Total Closure: {TOTAL_EYES_CLS}', FONTS, 0.7, (30,200),2)
                utils.colorBackgroundText(frame,  f'Total Winks: {TOTAL_WINK}', FONTS, 0.7, (30,250),2)
                utils.colorBackgroundText(frame,  f'RX_THRESHOLD: {rx_eye_threshold}' + f'LX_TRESHOLD: {lx_eye_threshold}', FONTS, 0.7, (30,300),2)
                utils.colorBackgroundText(frame,  f'RX_VALUE: {rvDistance}' + f'LX_VALUE: {rvDistance}', FONTS, 0.7, (30,350),2)
                utils.colorBackgroundText(frame,  f'Total Three Times Closure: {three_time_counter}', FONTS, 0.7, (30,400),2)

                cv.polylines(frame,  [np.array([mesh_coords[p] for p in LEFT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
                cv.polylines(frame,  [np.array([mesh_coords[p] for p in RIGHT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)



            # calculating  frame per seconds FPS
            end_time = time.time()-start_time
            fps = frame_counter/end_time

            frame =utils.textWithBackground(frame,f'FPS: {round(fps,1)}',FONTS, 1.0, (30, 50), bgOpacity=0.9, textThickness=2)
            # writing image for thumbnail drawing shape
            # cv.imwrite(f'img/frame_{frame_counter}.png', frame)
            cv.imshow('frame', frame)
            key = cv.waitKey(2)
            if key==ord('q') or key ==ord('Q'):
                break
        cv.destroyAllWindows()
        cap.release()
        calib_eyes_file.close()






def eyes_calib():
    """
    This function is used in order to tune the threshold parameter to detected eyes blinking
    @return: 
    """
    with map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:

        global frame_counter
        # starting time here 
        start_time = time.time()

        #StopWatch to count the time needed for the calibration
        timer_start = StopWatch()
        timer_start.start()

        print("Eyes Calibration Started")
        # starting Video loop here.
        while timer_start.elapsed_time < 10000: #10 seconds calibration
            frame_counter +=1 # frame counter
            ret, frame = camera.read() # getting frame from camera 
            if not ret: 
                break # no more frames break
            #  resizing frame
            
            frame = cv.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)
            frame_height, frame_width= frame.shape[:2]
            rgb_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
            results  = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                mesh_coords = landmarksDetection(frame, results, False)
                ratio,lvDistance,rvDistance = blinkRatio(frame, mesh_coords, RIGHT_EYE, LEFT_EYE)
                calib_eyes_file.write(str(lvDistance) + '\n')
                calib_eyes_file.write(str(rvDistance) + '\n')
                lv_eye.append(lvDistance)
                rv_eye.append(rvDistance)

                time_remained = "{:.2f}".format(10. - (timer_start.elapsed_time/1000))
                
                utils.colorBackgroundText(frame,  f'Time Remained: {time_remained}', FONTS, 0.7, (30,100),2)
                
                cv.polylines(frame,  [np.array([mesh_coords[p] for p in LEFT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
                cv.polylines(frame,  [np.array([mesh_coords[p] for p in RIGHT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)



            # calculating  frame per seconds FPS
            end_time = time.time()-start_time
            fps = frame_counter/end_time

            frame =utils.textWithBackground(frame,f'FPS: {round(fps,1)}',FONTS, 1.0, (30, 50), bgOpacity=0.9, textThickness=2)
            # writing image for thumbnail drawing shape
            # cv.imwrite(f'img/frame_{frame_counter}.png', frame)
            cv.imshow('Eyes Detection', frame)
            key = cv.waitKey(2)
            if key==ord('q') or key ==ord('Q'):
                break
       
        cv.destroyAllWindows()
        camera.release()
        calib_eyes_file.close()
        print("Eyes Calibration Finished")

        #Process the acquired data to compute the custom eye blink threshold
        max_lv_eye = np.max(lv_eye)
        min_lv_eye = np.min(lv_eye)
        max_rv_eye = np.max(rv_eye)
        min_rv_eye = np.min(rv_eye)
        lx_eye_range= max_lv_eye - min_lv_eye
        rx_eye_range = max_rv_eye - min_rv_eye
        
        #Compute 20% of the range
        lx_eye_percent = 0.3 * lx_eye_range
        rx_eye_percent = 0.3 * rx_eye_range

        #Add these to the minimum and return the values
        lx_eye_threshold = min_lv_eye + lx_eye_percent
        rx_eye_threshold = min_rv_eye + rx_eye_percent

        return lx_eye_threshold, rx_eye_threshold

        
