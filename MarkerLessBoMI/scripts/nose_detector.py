import cv2 as cv
import mediapipe as mp
import time , math,os,threading
from scripts.eye_blink_detector import NOSE_TIP
from scripts.stopwatch import StopWatch
from scripts import utils
import numpy as np

#open eyes_cls_calib
path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\calib\\nose_calib.txt"
calib_nose_file = open(path,"w+")

#Init Mediapipe face mesh
map_face_mesh = mp.solutions.face_mesh


# camera object 
camera = cv.VideoCapture(0)

# variables 
frame_counter = 0
nose_x_components = []
nose_y_components = []

FONTS =cv.FONT_HERSHEY_COMPLEX

# landmark detection function 
def landmarksDetection(img, results, draw=False):
    img_height, img_width= img.shape[:2]
    # list[(x,y), (x,y)....]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw :
        [cv.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    # returning the list of tuples for each landmarks 
    return mesh_coord

def nose_calib():
    """
    This function is used to establish a threshold for the nose to used it to change state of the FSM
    between base teleoperation and arm teleoperation
    @return:   
        nose_thresh: the nose threshold computed during the 10 seconds of calibration
    """
    global frame_counter,nose_x_components,nose_y_components
    
    with map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:
        # starting time here 
        start_time = time.time()

        #StopWatch to count the time needed for the calibration
        timer_start = StopWatch()
        timer_start.start()

        print("Nose Calibration Started")
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
                #Extract the mesh coordinates
                mesh_coords = landmarksDetection(frame, results, False)
            
                #Extract the point on the nose
                nose = mesh_coords[NOSE_TIP[0]]
                nose_x_components.append(nose[0])
                nose_y_components.append(nose[1])
                calib_nose_file.write(str(nose) + "\n")
                time_remained = "{:.2f}".format(10. - (timer_start.elapsed_time/1000))
                utils.colorBackgroundText(frame,  f'Time Remained: {time_remained}', FONTS, 0.7, (30,100),2)

                #Draw a red circle on the tip of the nose
                cv.circle(frame,(nose[0],nose[1]),radius=5,color=utils.RED,thickness=-1)

            # calculating  frame per seconds FPS
            end_time = time.time()-start_time
            fps = frame_counter/end_time

            frame =utils.textWithBackground(frame,f'FPS: {round(fps,1)}',FONTS, 1.0, (30, 50), bgOpacity=0.9, textThickness=2)
            # writing image for thumbnail drawing shape
            # cv.imwrite(f'img/frame_{frame_counter}.png', frame)
            cv.imshow('Nose Detection', frame)
            key = cv.waitKey(2)
            if key==ord('q') or key ==ord('Q'):
                break
       
        max_x_component = np.max(nose_x_components)
        min_x_component = np.min(nose_y_components)

        x_component_range = max_x_component - min_x_component
        x_range_percentage = x_component_range * .35
        nose_threshold = min_x_component + x_range_percentage

        cv.destroyAllWindows()
        camera.release()
        calib_nose_file.close()
        print("Nose Calibration Finished")
        return nose_threshold