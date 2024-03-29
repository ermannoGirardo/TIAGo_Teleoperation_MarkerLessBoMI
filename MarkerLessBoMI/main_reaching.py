# General imports
from asyncio.windows_events import CONNECT_PIPE_INIT_DELAY
from dis import dis
from doctest import BLANKLINE_MARKER
from email.mime import base
from socket import fromshare
import sys
from tracemalloc import stop
from turtle import color
from unittest import result
import numpy as np
from numpy import asarray,savetxt
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
# For multithreading
from threading import Thread, Lock
import queue
# For OpenCV
import cv2
# For GUI
import tkinter as tk
from tkinter import Label, Button, BooleanVar, Checkbutton, Text
from PIL import ImageTk, Image  

import math

# For pygame
import pygame
from sklearn.metrics import RocCurveDisplay
from scripts import nose_detector
from scripts.nose_detector import nose_calib
# For reaching task
from scripts.reaching import Reaching
from scripts.stopwatch import StopWatch
from scripts.filter_butter_online import FilterButter3

from scripts import reaching_functions
# For controlling computer cursor
import pyautogui
# For Mediapipe
import mediapipe as mp
# For training pca/autoencoder
from scripts.compute_bomi_map import Autoencoder, PrincipalComponentAnalysis, compute_vaf

#For display the webcam
from scripts.display_webcam import show_webcam

#For socket communication
from scripts.socket_client import *

#For eye blinkin detection
from  scripts.eye_blink_detector import *


pyautogui.PAUSE = 0.01  # set fps of cursor to 100Hz ish when mouse_enabled is True

#GLOBAL VARIABLES
lx_threshold = 0
rx_threshold = 0



# left_mouse_click variable is managed by eyes closure
# closing eyes for 1 seconds corresponds to click the mouse
# clicking the mouse on the odom GUI will publish a target for TIAGo
left_mouse_click = False


holistic = None
cap = None


#Take into account the state of the base teleoperation
#base_state_teleop == True --> 'nine region GUI'
#base_state_teleop == False --> 'odom GUI'
base_state_teleop = None


# --- MACROS FOR EXEC BASH FILE ---#
SIMPLE_OFFICE = "simple_office"
SIMPLE_OFFICE_WITH_PEOPLE = "simple_office_with_people"
REAL_TIAGO = "real_tiago"

# -- To store the controlling type -- #
controlling = ""


class MainApplication(tk.Frame):
    """
    class that defines the main tkinter window --> graphic with buttons etc..
    """

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.calibPath = os.path.dirname(os.path.abspath(__file__)) + "/calib/"
        self.drPath = ''
        self.num_joints = 0
        self.joints = np.zeros((5, 1))
        self.dr_mode = 'pca'
        self.font_size = 18
        self.num_PCA_components = 0

        self.btn_num_joints = Button(parent, text="Select Joints", command=self.select_joints)
        self.btn_num_joints.config(font=("Arial", self.font_size))
        self.btn_num_joints.grid(row=0, column=0, columnspan=2, padx=20, pady=30, sticky='nesw')

        # set checkboxes for selecting joints
        self.check_nose = BooleanVar()
        self.check1 = Checkbutton(win, text="Nose", variable=self.check_nose)
        self.check1.config(font=("Arial", self.font_size))
        self.check1.grid(row=0, column=2, padx=(0, 40), pady=30, sticky='w')

        self.check_eyes = BooleanVar()
        self.check2 = Checkbutton(win, text="Eyes", variable=self.check_eyes)
        self.check2.config(font=("Arial", self.font_size))
        self.check2.grid(row=0, column=3, padx=(0, 40), pady=30, sticky='w')

        self.check_shoulders = BooleanVar()
        self.check3 = Checkbutton(win, text="Shoulders", variable=self.check_shoulders)
        self.check3.config(font=("Arial", self.font_size))
        self.check3.grid(row=0, column=4, padx=(0, 30), pady=30, sticky='w')

        self.check_forefinger = BooleanVar()
        self.check4 = Checkbutton(win, text="Right Forefinger",
                                  variable=self.check_forefinger)
        self.check4.config(font=("Arial", self.font_size))
        self.check4.grid(row=0, column=5, padx=(0, 20), pady=30, sticky='w')

        self.check_fingers = BooleanVar()
        self.check5 = Checkbutton(win, text="Fingers", variable=self.check_fingers)
        self.check5.config(font=("Arial", self.font_size))
        self.check5.grid(row=0, column=6, padx=(0, 20), pady=30, sticky='nesw')

        self.btn_num_components = Button(parent, text="Select Components", command=self.select_components)
        self.btn_num_components.config(font=("Arial", self.font_size))
        self.btn_num_components.grid(row=1, column=0, columnspan=2, padx=20, pady=30, sticky='nesw')

        self.check_2D = BooleanVar()
        self.check_2D_button = Checkbutton(win, text="2D", variable=self.check_2D)
        self.check_2D_button.config(font=("Arial", self.font_size))
        self.check_2D_button.grid(row=1, column=2, padx=(0, 20), pady=30, sticky='nesw')

        self.check_3D = BooleanVar()
        self.check_3D_button = Checkbutton(win, text="3D", variable=self.check_3D)
        self.check_3D_button.config(font=("Arial", self.font_size))
        self.check_3D_button.grid(row=1, column=3, padx=(0, 20), pady=30, sticky='nesw')

        self.btn_calib = Button(parent, text="Calibration", command=self.calibration)
        self.btn_calib["state"] = "disabled"
        self.btn_calib.config(font=("Arial", self.font_size))
        self.btn_calib.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')
        self.calib_duration = 30000

        #Eyes Calibration Button
        self.btn_eyes_calib = Button(parent, text="Eyes Calibration", command=self.eyes_calibration)
        self.btn_eyes_calib["state"] = "normal"
        self.btn_eyes_calib.config(font=("Arial", self.font_size))
        self.btn_eyes_calib.grid(row=3, column=6, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        #Nose Calibration Button
        self.btn_eyes_calib = Button(parent, text="Nose Calibration", command=self.nose_calibration)
        self.btn_eyes_calib["state"] = "normal"
        self.btn_eyes_calib.config(font=("Arial", self.font_size))
        self.btn_eyes_calib.grid(row=4, column=6, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        #Show webcam button
        self.btn_webcam = Button(parent,text="Show Webcam",command=self.disp_webcam,bg="blue")
        self.btn_webcam.config(font=("Arial", self.font_size))
        self.btn_webcam.grid(row=2, column=6, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        #Label to close webcam display
        self.cls_webcam = Label(win, text=' Press esc to close')
        self.cls_webcam.config(font=("Arial", 15))
        self.cls_webcam.grid(row=2, column=8, columnspan=2, pady=(20, 30), sticky='w')

        # Calibration time remaining
        self.lbl_calib = Label(win, text='Calibration time: ')
        self.lbl_calib.config(font=("Arial", self.font_size))
        self.lbl_calib.grid(row=2, column=2, columnspan=2, pady=(20, 30), sticky='w')

        # BoMI map button and checkboxes
        self.btn_map = Button(parent, text="Calculate BoMI Map", command=self.train_map)
        self.btn_map["state"] = "disabled"
        self.btn_map.config(font=("Arial", self.font_size))
        self.btn_map.grid(row=3, column=0, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        self.check_pca = BooleanVar(value=True)
        self.check_pca1 = Checkbutton(win, text="PCA", variable=self.check_pca)
        self.check_pca1.config(font=("Arial", self.font_size))
        self.check_pca1.grid(row=3, column=2, padx=(0, 20), pady=(20, 30), sticky='w')

        self.check_ae = BooleanVar()
        self.check_ae1 = Checkbutton(win, text="AE", variable=self.check_ae)
        self.check_ae1.config(font=("Arial", self.font_size))
        self.check_ae1.grid(row=3, column=3, padx=(0, 20), pady=(20, 30), sticky='w')

        self.check_vae = BooleanVar()
        self.check_vae1 = Checkbutton(win, text="Variational AE", variable=self.check_vae)
        self.check_vae1.config(font=("Arial", self.font_size))
        self.check_vae1.grid(row=3, column=4, pady=(20, 30), sticky='w')

        self.btn_custom = Button(parent, text="Customization", command=self.customization)
        self.btn_custom["state"] = "disabled"
        self.btn_custom.config(font=("Arial", self.font_size))
        self.btn_custom.grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        self.btn_start = Button(parent, text="Practice", command=self.start)
        self.btn_start["state"] = "disabled"
        self.btn_start.config(font=("Arial", self.font_size))
        self.btn_start.grid(row=5, column=0, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        #Practice 3D Button 
        self.btn_3D_start = Button(parent, text="3D Practice", command=self.start_3D)
        self.btn_3D_start["state"] = "disabled"
        self.btn_3D_start.config(font=("Arial", self.font_size))
        self.btn_3D_start.grid(row=6, column=0, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

        self.btn_tiago_prt = Button(parent,text="TIAGo Practice",command=self.tiago_prt)
        self.btn_tiago_prt["state"] = "normal"
        self.btn_tiago_prt.config(font=("Arial", self.font_size))
        self.btn_tiago_prt.grid(row=5, column=6, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')


        # set label for number of target remaining
        self.lbl_tgt = Label(win, text='Remaining targets: ')
        self.lbl_tgt.config(font=("Arial", self.font_size))
        self.lbl_tgt.grid(row=5, column=2, pady=(20, 30), columnspan=2, sticky='w')

        # !!!!!!!!!!!!! [ADD CODE HERE] Mouse control checkbox !!!!!!!!!!!!!
        

        #############################################################

        self.btn_close = Button(parent, text="Close", command=parent.destroy, bg="red")
        self.btn_close.config(font=("Arial", self.font_size))
        self.btn_close.grid(row=9, column=0, columnspan=2, padx=20, pady=(20, 30), sticky='nesw')

    # Count number of joints selected
    def select_joints(self):
        nose_enabled = self.check_nose.get()
        eyes_enabled = self.check_eyes.get()
        shoulders_enabled = self.check_shoulders.get()
        forefinger_enabled = self.check_forefinger.get()
        fingers_enabled = self.check_fingers.get()
        if nose_enabled:
            self.num_joints += 2
            self.joints[0, 0] = 1
        if eyes_enabled:
            self.num_joints += 4
            self.joints[1, 0] = 1
        if shoulders_enabled:
            self.num_joints += 4
            self.joints[2, 0] = 1
        if forefinger_enabled:
            self.num_joints += 2
            self.joints[3, 0] = 1
        if fingers_enabled:
            self.num_joints += 10
            self.joints[4, 0] = 1
        if np.sum(self.joints, axis=0) != 0:
            self.btn_calib["state"] = "normal"
            self.btn_map["state"] = "normal"
            self.btn_custom["state"] = "normal"
            self.btn_start["state"] = "disabled"
            self.btn_3D_start["state"] = "disabled"
            print('Joints correctly selected.')

    def select_components(self):
        """
        Function used to track the number of component the user wants to use for reaching task
        """

        components_2D = self.check_2D.get()
        components_3D = self.check_3D.get()
        pca_calib_path = os.path.dirname(os.path.abspath(__file__)) + "/calib/" + "/PCA/"
        offset_file = open(pca_calib_path+"offset_custom.txt","w")
        scale_file = open(pca_calib_path + "scale_custom.txt","w")
        # no one checkboxes 
        if not components_2D and not components_3D:
            print("Please select at least one box")
            self.btn_calib["state"] = "disabled"
            self.btn_map["state"] = "disabled"
            self.btn_custom["state"] = "disabled"
            self.btn_start["state"] = "disabled"
            self.btn_3D_start["state"] = "disabled"
        
        #both checkboxes
        if components_2D and components_3D:
            print("Please select only one box")
            self.btn_calib["state"] = "disabled"
            self.btn_map["state"] = "disabled"
            self.btn_custom["state"] = "disabled"
            self.btn_start["state"] = "disabled"
            self.btn_3D_start["state"] = "disabled"
        
        #2D component
        if components_2D and not components_3D:
            self.num_PCA_components = 2
            self.btn_calib["state"] = "normal"
            self.btn_map["state"] = "normal"
            self.btn_custom["state"] = "normal"
            self.btn_start["state"] = "normal"
            self.btn_3D_start["state"] = "disabled"
            print("You have selected 2 components")
            offset_file.write("5.000000000000000000e+01\n0.000000000000000000e+00\n")
            scale_file.write("1.000000000000000000e+00\n1.000000000000000000e+00\n")

        #3D component
        elif components_3D and not components_2D:
            self.num_PCA_components = 3
            self.btn_calib["state"] = "normal"
            self.btn_map["state"] = "normal"
            self.btn_custom["state"] = "normal"
            self.btn_3D_start["state"] = "normal"
            self.btn_start["state"] = "disabled"
            print("You have selected 3 components")
            offset_file.write("5.000000000000000000e+01\n0.000000000000000000e+00\n0.000000000000000000e+00\n")
            scale_file.write("1.000000000000000000e+00\n1.000000000000000000e+00\n0.000000000000000000e+00\n")

        offset_file.close()
        scale_file.close()
    def calibration(self):
        # start calibration dance - collect webcam data
        self.w = popupWindow(self.master, "You will now start calibration.")
        self.master.wait_window(self.w.top)
        compute_calibration(self.calibPath, self.calib_duration, self.lbl_calib, self.num_joints, self.joints)
        self.btn_map["state"] = "normal"

    def eyes_calibration(self):
        global lx_threshold, rx_threshold
        # start calibration eyes  dance - collect webcam data
        self.w = popupWindow(self.master, "You will now start eyes calibration.")
        self.master.wait_window(self.w.top)
        lx_threshold, rx_threshold= eyes_calib()
        self.btn_tiago_prt["state"] = "normal"

    def nose_calibration(self):
        global nose_threshold
        self.w = popupWindow(self.master, "You will now start nose calibration.")
        self.master.wait_window(self.w.top)
        nose_threshold =nose_calib()
        self.btn_tiago_prt["state"] = "normal"

    def train_map(self):
        # check whether calibration file exists first
        if os.path.isfile(self.calibPath + "Calib.txt"):
            self.w = popupWindow(self.master, "You will now train BoMI map")
            self.master.wait_window(self.w.top)
            if self.check_pca.get():
                self.drPath = self.calibPath + 'PCA/'
                train_pca(self.calibPath, self.drPath,self.num_PCA_components)
                self.dr_mode = 'pca'
            elif self.check_ae.get():
                self.drPath = self.calibPath + 'AE/'
                train_ae(self.calibPath, self.drPath)
                self.dr_mode = 'ae'
            elif self.check_vae.get():
                self.drPath = self.calibPath + 'AE/'
                train_ae(self.calibPath, self.drPath)
                self.dr_mode = 'ae'
            self.btn_custom["state"] = "normal"
        else:
            self.w = popupWindow(self.master, "Perform calibration first.")
            self.master.wait_window(self.w.top)
            self.btn_map["state"] = "disabled"

    def customization(self):
        # check whether PCA/AE parameters have been saved
        if os.path.isfile(self.drPath + "weights1.txt"):
            # open customization window
            self.newWindow = tk.Toplevel(self.master)
            self.newWindow.geometry("1000x500")
            self.newWindow.title("Customization")
            self.app = CustomizationApplication(self.newWindow, self, drPath=self.drPath, num_joints=self.num_joints,
                                                joints=self.joints, dr_mode=self.dr_mode,pca_components=self.num_PCA_components)
        else:
            self.w = popupWindow(self.master, "Compute BoMI map first.")
            self.master.wait_window(self.w.top)
            self.btn_custom["state"] = "disabled"
    
    #TIAGo practice botton callback

    def start(self):
        # check whether customization parameters have been saved
        if os.path.isfile(self.drPath + "offset_custom.txt"):
            # open pygame and start reaching task
            self.w = popupWindow(self.master, "You will now start practice.")
            self.master.wait_window(self.w.top)
            start_reaching(self.drPath, self.lbl_tgt, self.num_joints, self.joints, self.dr_mode)
            # [ADD CODE HERE: one of the argument of start reaching should be [self.check_mouse]
            # to check in the checkbox is enable] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        else:
            self.w = popupWindow(self.master, "Perform customization first.")
            self.master.wait_window(self.w.top)
            self.btn_start["state"] = "disabled"

    #3D Practice Function Callback
    def start_3D(self):
        # check whether customization parameters have been saved
        if os.path.isfile(self.drPath + "offset_custom.txt"):
            # open pygame and start reaching task
            self.w = popupWindow(self.master, "You will now start practice.")
            self.master.wait_window(self.w.top)
            start_3D_reaching(self.drPath, self.lbl_tgt, self.num_joints, self.joints, self.dr_mode)
            # [ADD CODE HERE: one of the argument of start reaching should be [self.check_mouse]
            # to check in the checkbox is enable] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        else:
            self.w = popupWindow(self.master, "Perform customization first.")
            self.master.wait_window(self.w.top)
            self.btn_start["state"] = "disabled"

   #TIAGo practice botton callback
    def tiago_prt(self):
        # check whether PCA/AE parameters have been saved
        if os.path.isfile(self.drPath + "weights1.txt"):
            # open customization window
            self.newWindow = tk.Toplevel(self.master)
            self.newWindow.geometry("1000x500")
            self.newWindow.title("TIAGo Practice")
            self.app = TIAGoPracticeApplication(self.newWindow, self, drPath=self.drPath, num_joints=self.num_joints,
                                                joints=self.joints, dr_mode=self.dr_mode)

        else:
            self.w = popupWindow(self.master, "Compute BoMI map first.")
            self.master.wait_window(self.w.top)
            self.btn_custom["state"] = "disabled"

    #Function callback to display the webcam
    def disp_webcam(self):
        show_webcam(mirror=True)


class CustomizationApplication(tk.Frame):
    """
    class that defines the customization tkinter window
    """

    def __init__(self, parent, mainTk, drPath, num_joints, joints, dr_mode,pca_components):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.mainTk = mainTk
        self.drPath = drPath
        self.num_joints = num_joints
        self.joints = joints
        self.dr_mode = dr_mode
        self.font_size = 18
        self.position_checkboxes = 0

        if pca_components == 2:
            self.position_checkboxes = 3
        else:
            self.position_checkboxes = 4

        self.lbl_rot = Label(parent, text='Rotation ')
        self.lbl_rot.config(font=("Arial", self.font_size))
        self.lbl_rot.grid(column=0, row=0, padx=(300, 0), pady=(40, 20), sticky='w')
        self.txt_rot = Text(parent, width=10, height=1)
        self.txt_rot.config(font=("Arial", self.font_size))
        self.txt_rot.grid(column=1, row=0, pady=(40, 20))
        self.txt_rot.insert("1.0", '0')

        self.lbl_gx = Label(parent, text='Gain x ')
        self.lbl_gx.config(font=("Arial", self.font_size))
        self.lbl_gx.grid(column=0, row=1, padx=(300, 0), pady=(40, 20), sticky='w')
        self.txt_gx = Text(parent, width=10, height=1)
        self.txt_gx.config(font=("Arial", self.font_size))
        self.txt_gx.grid(column=1, row=1, pady=(40, 20))
        self.txt_gx.insert("1.0", '1')

        self.lbl_gy = Label(parent, text='Gain y ')
        self.lbl_gy.config(font=("Arial", self.font_size))
        self.lbl_gy.grid(column=0, row=2, padx=(300, 0), pady=(40, 20), sticky='w')
        self.txt_gy = Text(parent, width=10, height=1)
        self.txt_gy.config(font=("Arial", self.font_size))
        self.txt_gy.grid(column=1, row=2, pady=(40, 20))
        self.txt_gy.insert("1.0", '1')

        if pca_components == 3:
            self.lbl_gz = Label(parent, text='Gain z ')
            self.lbl_gz.config(font=("Arial", self.font_size))
            self.lbl_gz.grid(column=0, row=3, padx=(300, 0), pady=(40, 20), sticky='w')
            self.txt_gz = Text(parent, width=10, height=1)
            self.txt_gz.config(font=("Arial", self.font_size))
            self.txt_gz.grid(column=1, row=3, pady=(40, 20))
            self.txt_gz.insert("1.0", '1')

        self.lbl_ox = Label(parent, text='Offset x ')
        self.lbl_ox.config(font=("Arial", self.font_size))
        self.lbl_ox.grid(column=0, row=self.position_checkboxes, padx=(300, 0), pady=(40, 20), sticky='w')
        self.txt_ox = Text(parent, width=10, height=1)
        self.txt_ox.config(font=("Arial", self.font_size))
        self.txt_ox.grid(column=1, row=self.position_checkboxes, pady=(40, 20))
        self.txt_ox.insert("1.0", '0')

        self.lbl_oy = Label(parent, text='Offset y ')
        self.lbl_oy.config(font=("Arial", self.font_size))
        self.lbl_oy.grid(column=0, row=self.position_checkboxes+1, padx=(300, 0), pady=(40, 20), sticky='w')
        self.txt_oy = Text(parent, width=10, height=1)
        self.txt_oy.config(font=("Arial", self.font_size))
        self.txt_oy.grid(column=1, row=self.position_checkboxes+1, pady=(40, 20))
        self.txt_oy.insert("1.0", '0')

        if pca_components == 3:
            self.lbl_oz = Label(parent, text='Offset z ')
            self.lbl_oz.config(font=("Arial", self.font_size))
            self.lbl_oz.grid(column=0, row=self.position_checkboxes + 2, padx=(300, 0), pady=(40, 20), sticky='w')
            self.txt_oz = Text(parent, width=10, height=1)
            self.txt_oz.config(font=("Arial", self.font_size))
            self.txt_oz.grid(column=1, row=self.position_checkboxes + 2, pady=(40, 20))
            self.txt_oz.insert("1.0", '0')

        self.btn_save = Button(parent, text="Save parameters", command=self.save_parameters)
        self.btn_save.config(font=("Arial", self.font_size))
        self.btn_save.grid(column=2, row=1, sticky='nesw', padx=(80, 0), pady=(40, 20))

        self.btn_start = Button(parent, text="Start", command=self.customization)
        self.btn_start.config(font=("Arial", self.font_size))
        self.btn_start.grid(column=2, row=2, sticky='nesw', padx=(80, 0), pady=(40, 20))

        self.btn_close = Button(parent, text="Close", command=parent.destroy, bg='red')
        self.btn_close.config(font=("Arial", self.font_size))
        self.btn_close.grid(column=2, row=3, sticky='nesw', padx=(80, 0), pady=(40, 20))

    # functions to retrieve values of textbox programmatically
    def retrieve_txt_rot(self):
        return self.txt_rot.get("1.0", "end-1c")

    def retrieve_txt_gx(self):
        return self.txt_gx.get("1.0", "end-1c")

    def retrieve_txt_gy(self):
        return self.txt_gy.get("1.0", "end-1c")

    def retrieve_txt_ox(self):
        return self.txt_ox.get("1.0", "end-1c")

    def retrieve_txt_oy(self):
        return self.txt_oy.get("1.0", "end-1c")

    def customization(self):
        initialize_customization(self, self.dr_mode, self.drPath, self.num_joints, self.joints)

    def save_parameters(self):
        save_parameters(self, self.drPath)
        self.parent.destroy()
        self.mainTk.btn_start["state"] = "normal"

class TIAGoPracticeApplication(tk.Frame):
    """
    Class that define the popup win for TIAGo practice
    """
    def __init__(self, parent, mainTk, drPath, num_joints, joints, dr_mode):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.mainTk = mainTk
        self.drPath = drPath
        self.num_joints = num_joints
        self.joints = joints
        self.dr_mode = dr_mode
        self.font_size = 18
        self.selected_map = None

        #////////////////////TKINTER GUI///////////////////////////# 

        #Add an image to the background
        self.TIAGo_robot_img = Image.open(os.path.dirname(os.path.abspath(__file__)) + "\\images\\TIAGo++.jpg")
        self.img = ImageTk.PhotoImage(self.TIAGo_robot_img.resize((300,500)))
        self.label = Label(parent,image=self.img)
        self.label.image = self.img
        self.label.place(x=1500,y=50)

        self.home_label = Label(parent,text='Here you can practice for teleoperating TIAGo',bg="red")
        self.home_label.config(font=("Arial", self.font_size))
        self.home_label.grid(column=0, row=4, padx=(300, 0), pady=(40, 20), sticky='w')

        self.btn_base_tiago = Button(parent, text="Mobile Base GUI", command=self.base_practice)
        self.btn_base_tiago["state"] = "normal"
        self.btn_base_tiago.config(font=("Arial", self.font_size))
        self.btn_base_tiago.grid(column=2, row=11, sticky='nesw', padx=(80, 0), pady=(40, 20))
        
        # self.help_base = Label(parent,text='Move the cursor trough the nine areas to select the wanted velocity')
        # self.help_base.config(font=("Arial", 12))
        # self.help_base.grid(column=0, row=11, padx=(300, 0), pady=(40, 20), sticky='w')

        self.simple_office = BooleanVar()
        self.chose_map1 = Checkbutton(parent, text="Simple Office", variable=self.simple_office)
        self.chose_map1.config(font=("Arial", self.font_size))
        self.chose_map1.grid(row=11, column=0, pady=(20, 30), sticky='w')

        self.simple_office_with_people = BooleanVar()
        self.chose_map2 = Checkbutton(parent, text="Simple Office With People", variable=self.simple_office_with_people)
        self.chose_map2.config(font=("Arial", self.font_size))
        self.chose_map2.grid(row=12, column=0, pady=(20, 30), sticky='w')

        self.real_tiago = BooleanVar()
        self.chose_map3 = Checkbutton(parent, text="Real TIAGo", variable=self.real_tiago)
        self.chose_map3.config(font=("Arial", self.font_size))
        self.chose_map3.grid(row=13, column=0, pady=(20, 30), sticky='w')

        self.btn_choose_map = Button(parent, text="Choose Map", command=self.choose_map)
        self.btn_choose_map["state"] = "normal"
        self.btn_choose_map.config(font=("Arial", self.font_size))
        self.btn_choose_map.grid(column=0, row=20, sticky='nesw', padx= 20, pady=(20, 30))

        self.btn_arm_tiago = Button(parent, text="Manipulator GUI", command=self.arm_practice)
        self.btn_arm_tiago["state"] = "normal"
        self.btn_arm_tiago.config(font=("Arial", self.font_size))
        self.btn_arm_tiago.grid(column=2, row=12, sticky='nesw', padx=(80, 0), pady=(40, 20))

        self.btn_free_mode = Button(parent, text="Free Mode GUIs", command=self.free_mode)
        self.btn_free_mode["state"] = "normal"
        self.btn_free_mode.config(font=("Arial", self.font_size))
        self.btn_free_mode.grid(column=2, row=13, sticky='nesw', padx=(80, 0), pady=(40, 20))
        # self.help_arm = Label(parent,text='Move the cursor to select the joint and use arrows to select its value')
        # self.help_arm.config(font=("Arial", 12))
        # self.help_arm.grid(column=0, row=12, padx=(300, 0), pady=(40, 20), sticky='w')

        self.btn_close = Button(parent, text="Close", command=parent.destroy, bg='red')
        self.btn_close.config(font=("Arial", self.font_size))
        self.btn_close.grid(column=2, row=25, sticky='nesw', padx=(80, 0), pady=(40, 20))

        #///////////////////////////////////////////////////////////////////////////////////////#

        #/////////////CONNECT WITH SERVER/////////////////////////////#
        #If parameter = True ---> start the connection
        #if parameter = False --> close connection
        manage_connection_server(True)

        #////////////////BUTTONS FUNCTION CALLBACK////////////////////////#


    def choose_map(self):
        if self.simple_office.get():
            self.selected_map = "Simple Office"
        elif self.simple_office_with_people.get():
            self.selected_map = "Simple Office With People"
        elif self.real_tiago.get():
            self.selected_map = "Real Tiago"
        print("Map Selected")

    def arm_practice(self):
        self.w = popupWindow(self.master, "You can now start practicing manipulation")
        self.master.wait_window(self.w.top)
        initialize_arm_practice(self, self.dr_mode, self.drPath, self.num_joints, self.joints)

    def base_practice(self):
        global lx_threshold, rx_threshold
        self.w = popupWindow(self.master, "You can now start practicing navigation")
        self.master.wait_window(self.w.top)

        #Initialize base_practice
        initialize_base_practice(self, self.dr_mode, self.drPath, self.num_joints, self.joints)
        
    def free_mode(self):
        self.w = popupWindow(self.master, "You can now start practicing manipulation")
        self.master.wait_window(self.w.top)
        initialize_free_mode(self, self.dr_mode, self.drPath, self.num_joints, self.joints)


class popupWindow(object):
    """
    class that defines the popup tkinter window
    """

    def __init__(self, master, msg):
        top = self.top = tk.Toplevel(master)
        self.lbl = Label(top, text=msg)
        self.lbl.pack()
        self.btn = Button(top, text='Ok', command=self.cleanup)
        self.btn.pack()

    def cleanup(self):
        self.top.destroy()


def compute_calibration(drPath, calib_duration, lbl_calib, num_joints, joints):
    """
    function called to collect calibration data from webcam
    :param drPath: path to save calibration file
    :param calib_duration: duration of calibration as read by the textbox in the main window
    :param lbl_calib: label in the main window that shows calibration time remaining
    :return:
    """
    # Create object of openCV and Reaching (needed for terminating mediapipe thread)
    cap = cv2.VideoCapture(0)
    r = Reaching()

    #video_calib_rec folder path
    rec_folder=os.path.dirname(os.path.abspath(__file__)) + "/video_calib_rec/"

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(rec_folder + 'output.avi', fourcc, 20.0, (640, 480))
 
    # The clock will be used to control how fast the screen updates. Stopwatch to count calibration time elapsed
    clock = pygame.time.Clock()
    timer_calib = StopWatch()

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    map_face_mesh = mp.solutions.face_mesh
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable
    body_calib = []  # initialize local variable (list of body landmarks during calibration)

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 1  # if cal==1 (meaning during calibration) the opencv thread will display the image
    # opencv_thread = Thread(target=save_video_calib, args=(cap, q_frame, r, cal))
    # opencv_thread.start()
    print("openCV thread started in calibration.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                              args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in calibration.")

    # start the timer for calibration
    timer_calib.start()

    print("main thread: Starting calibration...")
    
    with map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:
    
        while not r.is_terminated:

            if timer_calib.elapsed_time > calib_duration:
                r.is_terminated = True
            
            # reads frames from a camera 
            # ret checks return at each frame
            ret, frame = cap.read() 

            q_frame.put(frame)
                        
            # get current value of body
            body_calib.append(np.copy(body))

            # update time elapsed label
            time_remaining = int((calib_duration - timer_calib.elapsed_time) / 1000)
            lbl_calib.configure(text='Calibration time: ' + str(time_remaining))
            lbl_calib.update()

            # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
            #image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)     

            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            #frame = cv.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC)

            #Extract height and width
            frame_height, frame_width= frame.shape[:2]
        
            #Process holistic
            holistic_result = holistic.process(rgb_frame)

            #process face mesh
            face_mesh_results  = face_mesh.process(rgb_frame)
            
            if face_mesh_results.multi_face_landmarks:
                mesh_coords = landmarksDetection(rgb_frame, face_mesh_results, False)

            if holistic_result.pose_landmarks:
                #Extract all the points processed by Mediapipe
                right_shoulder_x = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER].x * frame_width
                right_shoulder_y = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER].y * frame_height
                left_shoulder_x = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER].x * frame_width
                left_shoulder_y = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER].y * frame_height
                nose_tip_x = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x * frame_width
                nose_tip_y = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y * frame_height
                left_eye_centre_x = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].x * frame_width
                left_eye_centre_y = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].y * frame_height
                right_eye_centre_x = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EYE].x * frame_width
                right_eye_centre_y = holistic_result.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EYE].y * frame_height



                #print all the points for shoulders nose tip and eyes

                #if shoulders are selected
                if joints[2, 0] == 1:
                    cv.circle(frame,(int(left_shoulder_x),int(left_shoulder_y)),radius=5,color=utils.RED,thickness=-1)
                    cv.circle(frame,(int(right_shoulder_x),int(right_shoulder_y)),radius=5,color=utils.RED,thickness=-1)
                
                #If nose is selected
                if joints[0, 0] == 1:
                    cv.circle(frame,(int(nose_tip_x),int(nose_tip_y)),radius=5,color=utils.RED,thickness=-1)
                
                #If eyes are selected
                if joints[1, 0] == 1:
                    cv.polylines(frame,  [np.array([mesh_coords[p] for p in LEFT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
                    cv.polylines(frame,  [np.array([mesh_coords[p] for p in RIGHT_EYE ], dtype=np.int32)], True, utils.GREEN, 1, cv.LINE_AA)
                    cv.circle(frame,(int(left_eye_centre_x),int(left_eye_centre_y)),radius=2,color=utils.RED,thickness=-1)
                    cv.circle(frame,(int(right_eye_centre_x),int(right_eye_centre_y)),radius=2,color=utils.RED,thickness=-1)


            # output the frame
            out.write(frame) 
            # The original input frame is shown in the window 
            cv2.imshow('Output', frame)
            
            # --- Limit to 50 frames per second
            clock.tick(50)

    # Stop the game engine and release the capture
    holistic.close()
    print("pose estimation object released in calibration.")
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("openCV object released in calibration.")

    # print calibration file
    body_calib = np.array(body_calib)
    if not os.path.exists(drPath):
        os.makedirs(drPath)
    np.savetxt(drPath + "Calib.txt", body_calib)

    print('Calibration finished. You can now train BoMI forward map.')


def train_pca(calibPath, drPath,PCA_num_components):
    """
    function to train BoMI forward map - PCA
    :param drPath: path to save BoMI forward map
    :return:
    """
    r = Reaching()
    # read calibration file and remove all the initial zero rows
    xp = list(pd.read_csv(calibPath + 'Calib.txt', sep=' ', header=None).values)
    x = [i for i in xp if all(i)]
    x = np.array(x)

    # randomly shuffle input
    np.random.shuffle(x)

    # define train/test split
    thr = 80
    split = int(len(x) * thr / 100)
    train_x = x[0:split, :]
    test_x = x[split:, :]

    # initialize object of class PCA
    if PCA_num_components == 2:   
        n_pc = 2
    elif PCA_num_components == 3:
        n_pc = 3

    PCA = PrincipalComponentAnalysis(n_pc)

    # train PCA
    pca, train_x_rec, train_pc, test_x_rec, test_pc = PCA.train_pca(train_x, x_test=test_x)
    print('PCA has been trained.')
    



    # save weights and biases
    if not os.path.exists(drPath):
        os.makedirs(drPath)
    
    if PCA_num_components == 2:
        np.savetxt(drPath + "weights1.txt", pca.components_[:, :2])
    elif PCA_num_components == 3:
        np.savetxt(drPath + "weights1.txt", pca.components_[:, :3])


    print('BoMI forward map (PCA parameters) has been saved.')

    # compute train/test VAF
    print(f'Training VAF: {compute_vaf(train_x, train_x_rec)}')
    print(f'Test VAF: {compute_vaf(test_x, test_x_rec)}')
    
    #Plot the explained variance ratio
    plt.bar(range(1,len(pca.explained_variance_ )+1),pca.explained_variance_ratio_ )
    plt.ylabel('Explained variance')
    plt.xlabel('Components')
    plt.plot(range(1,len(pca.explained_variance_ratio_ )+1),
         np.cumsum(pca.explained_variance_ratio_),
         c='red',
         label="Cumulative Explained Variance")
    plt.show()
    



    # normalize latent space to fit the monitor coordinates
    # Applying rotation

    if PCA_num_components == 2: 
        train_pc = np.dot(train_x, pca.components_[:, :2])  

        savetxt('PCA_Features.csv',train_pc,delimiter=',')


        rot = 0
        train_pc[0] = train_pc[0] * np.cos(np.pi / 180 * rot) - train_pc[1] * np.sin(np.pi / 180 * rot)
        train_pc[1] = train_pc[0] * np.sin(np.pi / 180 * rot) + train_pc[1] * np.cos(np.pi / 180 * rot)
        
        # Applying scale
        scale = [r.width / np.ptp(train_pc[:, 0]), r.height / np.ptp(train_pc[:, 1])]
        #scale = [r.width / np.ptp(train_pc[:, 0]), r.height / np.ptp(train_pc[:, 1]), r.depth / np.ptp(train_pc[:, 2])]
        train_pc = train_pc * scale
        # Applying offset
        off = [r.width / 2 - np.mean(train_pc[:, 0]), r.height / 2 - np.mean(train_pc[:, 1])]
        #off = [r.width / 2 - np.mean(train_pc[:, 0]), r.height / 2 - np.mean(train_pc[:, 1]), r.depth / 2 - np.mean(train_pc[:, 2])]
        train_pc = train_pc + off

    if PCA_num_components == 3:
        train_pc = np.dot(train_x, pca.components_[:, :3])  

        savetxt('PCA_Features.csv',train_pc,delimiter=',')


        rot = 0
        train_pc[0] = train_pc[0] * np.cos(np.pi / 180 * rot) - train_pc[1] * np.sin(np.pi / 180 * rot)
        train_pc[1] = train_pc[0] * np.sin(np.pi / 180 * rot) + train_pc[1] * np.cos(np.pi / 180 * rot)
        
        # Applying scale
        scale = [r.width / np.ptp(train_pc[:, 0]), r.height / np.ptp(train_pc[:, 1]),r.crs_range / np.ptp(train_pc[:,2])]
        #scale = [r.width / np.ptp(train_pc[:, 0]), r.height / np.ptp(train_pc[:, 1]), r.depth / np.ptp(train_pc[:, 2])]
        train_pc = train_pc * scale
        # Applying offset
        off = [r.width / 2 - np.mean(train_pc[:, 0]), r.height / 2 - np.mean(train_pc[:, 1]),r.crs_range / 2 - np.mean(train_pc[:,2])]
        #off = [r.width / 2 - np.mean(train_pc[:, 0]), r.height / 2 - np.mean(train_pc[:, 1]), r.depth / 2 - np.mean(train_pc[:, 2])]
        train_pc = train_pc + off

    # Plot latent space
    plt.figure()
    plt.scatter(train_pc[:, 0], train_pc[:, 1],c='green', s=20)
    #plt.scatter(train_pc[:, 0], train_pc[:, 1],train_pc[:,2],c='green', s=20)  
    plt.title('Projections in workspace')
    plt.axis("equal")

    # save AE scaling values
    with open(drPath + "rotation_dr.txt", 'w') as f:
        print(rot, file=f)
    np.savetxt(drPath + "scale_dr.txt", scale)
    np.savetxt(drPath + "offset_dr.txt", off)

    print('PCA scaling values has been saved. You can continue with customization.')


def train_ae(calibPath, drPath):
    """
    function to train BoMI forward map
    :param drPath: path to save BoMI forward map
    :return:
    """
    r = Reaching()

    # Autoencoder parameters
    n_steps = 3001
    lr = 0.02
    cu = 2
    nh1 = 6
    activ = "tanh"

    # read calibration file and remove all the initial zero rows
    xp = list(pd.read_csv(calibPath + 'Calib.txt', sep=' ', header=None).values)
    x = [i for i in xp if all(i)]
    x = np.array(x)

    # randomly shuffle input
    np.random.shuffle(x)

    # define train/test split
    thr = 80
    split = int(len(x) * thr / 100)
    train_x = x[0:split, :]
    test_x = x[split:, :]

    # initialize object of class Autoencoder
    AE = Autoencoder(n_steps, lr, cu, activation=activ, nh1=nh1, seed=0)

    # train AE network
    history, ws, bs, train_x_rec, train_cu, test_x_rec, test_cu = AE.train_network(train_x, x_test=test_x)
    # history, ws, bs, train_x_rec, train_cu, test_x_rec, test_cu = AE.train_vae(train_x, beta=0.00035, x_test=test_x)
    print('AE has been trained.')

    # save weights and biases
    if not os.path.exists(drPath):
        os.makedirs(drPath)
    for layer in range(3):
        np.savetxt(drPath + "weights" + str(layer + 1) + ".txt", ws[layer])
        np.savetxt(drPath + "biases" + str(layer + 1) + ".txt", bs[layer])

    print('BoMI forward map (AE parameters) has been saved.')

    # compute train/test VAF
    print(f'Training VAF: {compute_vaf(train_x, train_x_rec)}')
    print(f'Test VAF: {compute_vaf(test_x, test_x_rec)}')

    # normalize latent space to fit the monitor coordinates
    # Applying rotation
    rot = 0
    train_cu[0] = train_cu[0] * np.cos(np.pi / 180 * rot) - train_cu[1] * np.sin(np.pi / 180 * rot)
    train_cu[1] = train_cu[0] * np.sin(np.pi / 180 * rot) + train_cu[1] * np.cos(np.pi / 180 * rot)
    # Applying scale
    scale = [r.width / np.ptp(train_cu[:, 0]), r.height / np.ptp(train_cu[:, 1])]
    train_cu = train_cu * scale
    # Applying offset
    off = [r.width / 2 - np.mean(train_cu[:, 0]), r.height / 2 - np.mean(train_cu[:, 1])]
    train_cu = train_cu + off

    # Plot latent space
    plt.figure()
    plt.scatter(train_cu[:, 0], train_cu[:, 1], c='green', s=20)
    plt.title('Projections in workspace')
    plt.axis("equal")

    # save AE scaling values
    with open(drPath + "rotation_dr.txt", 'w') as f:
        print(rot, file=f)
    np.savetxt(drPath + "scale_dr.txt", scale)
    np.savetxt(drPath + "offset_dr.txt", off)

    print('AE scaling values has been saved. You can continue with customization.')


def load_bomi_map(dr_mode, drPath):
    if dr_mode == 'pca':
        map = pd.read_csv(drPath + 'weights1.txt', sep=' ', header=None).values
    elif dr_mode == 'ae':
        ws = []
        bs = []
        ws.append(pd.read_csv(drPath + 'weights1.txt', sep=' ', header=None).values)
        ws.append(pd.read_csv(drPath + 'weights2.txt', sep=' ', header=None).values)
        ws.append(pd.read_csv(drPath + 'weights3.txt', sep=' ', header=None).values)
        bs.append(pd.read_csv(drPath + 'biases1.txt', sep=' ', header=None).values)
        bs[0] = bs[0].reshape((bs[0].size,))
        bs.append(pd.read_csv(drPath + 'biases2.txt', sep=' ', header=None).values)
        bs[1] = bs[1].reshape((bs[1].size,))
        bs.append(pd.read_csv(drPath + 'biases3.txt', sep=' ', header=None).values)
        bs[2] = bs[2].reshape((bs[2].size,))

        map = (ws, bs)

    return map


def initialize_customization(self, dr_mode, drPath, num_joints, joints):
    """
    initialize objects needed for online cursor control. Start all the customization threads as well
    :param self: CustomizationApplication tkinter Frame. needed to retrieve textbox values programmatically
    :param drPath: path to load the BoMI forward map
    :return:
    """

    # Create object of openCV, Reaching class and filter_butter3
    cap = cv2.VideoCapture(0)
    r = Reaching()
    filter_curs = FilterButter3("lowpass_4")

    # initialize target position
    reaching_functions.initialize_targets(r)

    # load BoMI forward map parameters for converting body landmarks into cursor coordinates
    map = load_bomi_map(dr_mode, drPath)

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # load scaling values saved after training AE for covering entire monitor workspace
    rot = pd.read_csv(drPath + 'rotation_dr.txt', sep=' ', header=None).values
    scale = pd.read_csv(drPath + 'scale_dr.txt', sep=' ', header=None).values
    scale = np.reshape(scale, (scale.shape[0],))
    off = pd.read_csv(drPath + 'offset_dr.txt', sep=' ', header=None).values
    off = np.reshape(off, (off.shape[0],))

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 0
    opencv_thread = Thread(target=get_data_from_camera, args=(cap, q_frame, r, cal))
    opencv_thread.start()
    print("openCV thread started in customization.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                              args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in customization.")

    # Define some colors
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    CURSOR = (0.19 * 255, 0.65 * 255, 0.4 * 255)
    

    pygame.init()

    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    # Open a new window
    size = (r.width, r.height)
    screen = pygame.display.set_mode(size)
    # screen = pygame.display.toggle_fullscreen()

    # -------- Main Program Loop -----------
    while not r.is_terminated:
        # --- Main event loop
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                r.is_terminated = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                    r.is_terminated = True
                if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                    pyautogui.click(r.crs_x, r.crs_y)

        if not r.is_paused:
            # Copy old cursor position
            r.old_crs_x = r.crs_x
            r.old_crs_y = r.crs_y

            # get current value of body
            r.body = np.copy(body)

            # apply BoMI forward map to body vector to obtain cursor position
            r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

            # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
            try:
                rot_custom = int(self.retrieve_txt_rot())
            except:
                rot_custom = 0
            try:
                gx_custom = float(self.retrieve_txt_gx())
            except:
                gx_custom = 1.0
            try:
                gy_custom = float(self.retrieve_txt_gy())
            except:
                gy_custom = 1.0
            try:
                ox_custom = int(self.retrieve_txt_ox())
            except:
                ox_custom = 0
            try:
                oy_custom = int(self.retrieve_txt_oy())
            except:
                oy_custom = 0

            # Applying rotation
            r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
            r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
            # Applying scale
            r.crs_x = r.crs_x * gx_custom
            r.crs_y = r.crs_y * gy_custom
            # Applying offset
            r.crs_x = r.crs_x + ox_custom
            r.crs_y = r.crs_y + oy_custom

            # Limit cursor workspace
            if r.crs_x >= r.width:
                r.crs_x = r.width
            if r.crs_x <= 0:
                r.crs_x = 0
            if r.crs_y >= r.height:
                r.crs_y = 0
            if r.crs_y <= 0:
                r.crs_y = r.height

            # Filter the cursor
            r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

            # Set target position to update the GUI
            reaching_functions.set_target_reaching_customization(r)

            # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
            screen.fill(BLACK)

            # draw cursor
            pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

            # draw each test target
            for i in range(8):
                tgt_x = r.tgt_x_list[r.list_tgt[i]]
                tgt_y = r.tgt_y_list[r.list_tgt[i]]
                pygame.draw.circle(screen, GREEN, (int(tgt_x), int(tgt_y)), r.tgt_radius, 2)

            # --- update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 50 frames per second
            clock.tick(50)

    # Once we have exited the main program loop, stop the game engine and release the capture
    pygame.quit()
    print("game engine object released in customization.")
    holistic.close()
    print("pose estimation object released terminated in customization.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in customization.")


def initialize_base_practice(self, dr_mode, drPath, num_joints, joints):
    """
    initialize objects needed for online cursor control to teleoperate TIAGo mobile base.
    Start all the customization threads as well
    :param self: CustomizationApplication tkinter Frame. needed to retrieve textbox values programmatically
    :param drPath: path to load the BoMI forward map
    :param num_joints: the number of joints used to teleoperate TIAgo
    :param joints: type of joints used to teleoperate TIAGo
    """
    global holistic,cap, base_state_teleop,controlling,nose_threshold
    
    # --- SEND TO THE SERVER THE COMMAND TO EXECUTE THE CORRECT BASH FILE ---#
    if self.selected_map == 'Simple Office':
        bytes_to_send=parse_bash_file(SIMPLE_OFFICE)
        send_data(bytes_to_send)
        #update the map name into eye_blink_detector script
        update_map_name(self.selected_map)

    elif self.selected_map == "Simple Office With People":
        bytes_to_send=parse_bash_file(SIMPLE_OFFICE_WITH_PEOPLE)
        send_data(bytes_to_send)
        #update the map name into eye_blink_detector script
        update_map_name(self.selected_map)
    
    elif self.selected_map == "Real Tiago":
        bytes_to_send = parse_bash_file(REAL_TIAGO)
        send_data(bytes_to_send)    

    #Sleep 20 seconds in order to give time to Ubuntu to run all topics
    time.sleep(20)
    
    # Create object of openCV, Reaching class and filter_butter3
    cap = cv2.VideoCapture(0)
    r = Reaching()
    r.control_base = True
    controlling = "base"
    update_teleoperation_state(controlling)
    filter_curs = FilterButter3("lowpass_4")

    # initialize target position
    #reaching_functions.initialize_targets(r)

    # load BoMI forward map parameters for converting body landmarks into cursor coordinates
    print("La modalità inserita e':" +str(dr_mode))
    map = load_bomi_map(dr_mode, drPath)
    

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # load scaling values saved after training AE for covering entire monitor workspace
    rot = pd.read_csv(drPath + 'rotation_dr.txt', sep=' ', header=None).values
    scale = pd.read_csv(drPath + 'scale_dr.txt', sep=' ', header=None).values
    scale = np.reshape(scale, (scale.shape[0],))
    off = pd.read_csv(drPath + 'offset_dr.txt', sep=' ', header=None).values
    off = np.reshape(off, (off.shape[0],))

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 0
    opencv_thread = Thread(target=get_data_from_camera, args=(cap, q_frame, r, cal))
    opencv_thread.start()
    print("openCV thread started in customization.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                              args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in customization.")

    #Init Blinkinkg Eyes Detection
    init_blinking_detection(True,lx_threshold,rx_threshold, cap,nose_threshold)

    # Define some colors
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255,0,0)
    CURSOR = (0.19 * 255, 0.65 * 255, 0.4 * 255)
    WHITE = (255,255,255)

    #Define variables to create 'odom' GUI
    point_on_x_axis = np.linspace(0,1800,21)
    point_on_y_axis = np.linspace(0,900,15)

    neg_index = 10  
    pos_index = 1

    pygame.init()

    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    #Initialize stopwatch to control velocity selection
    timer_enter_region = StopWatch()

    # Open a new window
    size = (r.base_width, r.base_height)
    screen = pygame.display.set_mode(size)

    # -------- Main Program Loop -----------##
    while not r.is_terminated:
        if base_state.get() == False:
            base_state_teleop = True
            bytes_to_send=set_base_teleop_state(base_state_teleop)
            send_data(bytes_to_send)
            while base_state.empty():
                # --- Main Nine Regions GUI -- #
                for event in pygame.event.get():  # User did something
                    if event.type == pygame.QUIT:  # If user clicked close
                        r.is_terminated = True  # Flag that we are done so we exit this loop
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                            r.is_terminated = True
                        if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                            pyautogui.click(r.crs_x, r.crs_y)

                if not r.is_paused:
                    # Copy old cursor position
                    r.old_crs_x = r.crs_x
                    r.old_crs_y = r.crs_y

                    # get current value of body
                    r.body = np.copy(body)

                    # apply BoMI forward map to body vector to obtain cursor position
                    r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)


                    # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                    try:
                        rot_custom = int(self.retrieve_txt_rot())
                    except:
                        rot_custom = 0
                    try:
                        gx_custom = float(self.retrieve_txt_gx())
                    except:
                        gx_custom = 1.0
                    try:
                        gy_custom = float(self.retrieve_txt_gy())
                    except:
                        gy_custom = 1.0
                    try:
                        ox_custom = int(self.retrieve_txt_ox())
                    except:
                        ox_custom = 0
                    try:
                        oy_custom = int(self.retrieve_txt_oy())
                    except:
                        oy_custom = 0

                    # Applying rotation
                    r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                    r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                    # Applying scale
                    r.crs_x = r.crs_x * gx_custom
                    r.crs_y = r.crs_y * gy_custom
                    # Applying offset
                    r.crs_x = r.crs_x + ox_custom
                    r.crs_y = r.crs_y + oy_custom

                    # Limit cursor workspace
                    if r.crs_x >= r.base_width:
                        r.crs_x = r.base_width
                    if r.crs_x <= 0:
                        r.crs_x = 0
                    if r.crs_y >= r.base_height:
                        r.crs_y = 0
                    if r.crs_y <= 0:
                        r.crs_y = r.base_height

                    # Filter the cursor
                    r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

                    # Set target position to update the GUI
                    #reaching_functions.set_target_reaching_customization(r)

                    # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
                    screen.fill(BLACK)

                    # draw cursor
                    pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

                    # draw each separetor bar
                    pygame.draw.rect(screen,GREEN,pygame.Rect(600,0,5,900))
                    pygame.draw.rect(screen,GREEN,pygame.Rect(1200,0,5,900))
                    pygame.draw.rect(screen,GREEN,pygame.Rect(0,300,1800,5))
                    pygame.draw.rect(screen,GREEN,pygame.Rect(0,600,1800,5))
                
                    

                    # --- update region position 
                    reaching_functions.check_region_cursor(r,timer_enter_region)

                    #-- check stopwatch and compute velocities
                    reaching_functions.check_time_region(r,timer_enter_region)

                    #Log schermo
                    font = pygame.font.Font('freesansbold.ttf', 35)
                    stampa = "Lin Vel: " + str(r.lin_vel) + " Ang vel: " + str(r.ang_vel)
                    text4 = font.render(stampa,True,BLACK,GREEN)
                    textRect4 = text4.get_rect()
                    textRect4.center = (900,450)
                    screen.blit(text4,textRect4)



                    #parse the string to be send
                    bytes_string = parse_velocities(r)
                    send_data(bytes_string)

                    # --- update the screen with what we've drawn.
                    pygame.display.flip()

                    # --- Limit to 50 frames per second
                    clock.tick(50)

        else: 
            base_state_teleop = False
            bytes_to_send=set_base_teleop_state(base_state_teleop)
            send_data(bytes_to_send)
            while base_state.empty():
                # --- Main event loop Odom GUI ---#
                for event in pygame.event.get():  # User did something
                    if event.type == pygame.QUIT:  # If user clicked close
                        r.is_terminated = True  # Flag that we are done so we exit this loop
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                            r.is_terminated = True
                        if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                            pyautogui.click(r.crs_x, r.crs_y)

                if not r.is_paused:
                    # Copy old cursor position
                    r.old_crs_x = r.crs_x
                    r.old_crs_y = r.crs_y

                    # get current value of body
                    r.body = np.copy(body)

                    # apply BoMI forward map to body vector to obtain cursor position
                    r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

                    # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                    try:
                        rot_custom = int(self.retrieve_txt_rot())
                    except:
                        rot_custom = 0
                    try:
                        gx_custom = float(self.retrieve_txt_gx())
                    except:
                        gx_custom = 1.0
                    try:
                        gy_custom = float(self.retrieve_txt_gy())
                    except:
                        gy_custom = 1.0
                    try:
                        ox_custom = int(self.retrieve_txt_ox())
                    except:
                        ox_custom = 0
                    try:
                        oy_custom = int(self.retrieve_txt_oy())
                    except:
                        oy_custom = 0

                    # Applying rotation
                    r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                    r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                    # Applying scale
                    r.crs_x = r.crs_x * gx_custom
                    r.crs_y = r.crs_y * gy_custom
                    # Applying offset
                    r.crs_x = r.crs_x + ox_custom
                    r.crs_y = r.crs_y + oy_custom

                    # Limit cursor workspace
                    if r.crs_x >= r.base_width:
                        r.crs_x = r.base_width
                    if r.crs_x <= 0:
                        r.crs_x = 0
                    if r.crs_y >= r.base_height:
                        r.crs_y = 0
                    if r.crs_y <= 0:
                        r.crs_y = r.base_height

                    # Filter the cursor
                    r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)
                    update_mouse_coordinates(r)
                    

                    # Set target position to update the GUI
                    #reaching_functions.set_target_reaching_customization(r)

                    # First, clear the screen to white. In between screen.fill and pygame.display.flip() all the draw
                    screen.fill(WHITE)

                    # draw cursor
                    pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

                    neg_index = 10  
                    pos_index = 1

                    #draw numbers on the x-axis
                    font = pygame.font.Font('freesansbold.ttf', 20)
                    for x_coordinate in point_on_x_axis:
                        if x_coordinate < 900:
                            text = font.render( '-' + str(neg_index),True,BLACK,WHITE)
                            textRect = text.get_rect()
                            textRect.center = (x_coordinate,490)
                            screen.blit(text,textRect)
                            neg_index -= 1
                        if x_coordinate > 900:
                            text = font.render(str(pos_index),True,BLACK,WHITE)
                            textRect = text.get_rect()
                            textRect.center = (x_coordinate,490)
                            screen.blit(text,textRect)
                            pos_index += 1

                    pos_index = 7
                    neg_index = 1


                    #draw nubers on the y-axis
                    for y_coordinate in point_on_y_axis:
                        if y_coordinate > 500:
                            text = font.render( '-' + str(neg_index),True,BLACK,WHITE)
                            textRect = text.get_rect()
                            textRect.center = (930,y_coordinate)
                            screen.blit(text,textRect)
                            neg_index += 1
                        if y_coordinate < 450:
                            text = font.render(str(pos_index),True,BLACK,WHITE)
                            textRect = text.get_rect()
                            textRect.center = (930,y_coordinate)
                            screen.blit(text,textRect)
                            pos_index -= 1
                    

                    pygame.draw.rect(screen,BLACK,pygame.Rect(900,0,5,900))
                    pygame.draw.rect(screen,BLACK,pygame.Rect(0,450,1800,5))
        
                    # draw segment on x and y axes
                    for x_coordinate in point_on_x_axis:
                        pygame.draw.rect(screen,BLACK,pygame.Rect(x_coordinate,443,5,20))
            
                    for y_coordinate in point_on_y_axis:
                        pygame.draw.rect(screen,BLACK,pygame.Rect(893,y_coordinate,20,5))

                    # --- update the screen with what we've drawn.
                    pygame.display.flip()

                    # --- Limit to 50 frames per second
                    clock.tick(50)


    # Once we have exited the main program loop, stop the game engine and release the capture
    r.control_base = False
    controlling = ""
    update_teleoperation_state(controlling)
    pygame.quit()
    print("game engine object released in customization.")
    holistic.close()
    print("pose estimation object released terminated in customization.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in customization.")

    # #///////////CLOSE SOCKET COMMUNICATION////////#
    manage_connection_server(False)


def euclidian_distance(x,y):
    #Considering the centre of the axis 900,450
    x_center = 900
    y_center = 450
    distance = math.sqrt((x_center - x ) ** 2 + (y_center -y) ** 2)
    return distance

def compute_amplitude(alpha):
    amplitude = (1/150) * (alpha - 45) ** 2
    return amplitude

def initialize_arm_practice(self, dr_mode, drPath, num_joints, joints):
    """
    initialize objects needed for online cursor control to teleoperate TIAGo arm.
    Start all the customization threads as well
    :param self: CustomizationApplication tkinter Frame. needed to retrieve textbox values programmatically
    :param drPath: path to load the BoMI forward map
    :return:
    """
    global controlling,nose_threshold

    
    # --- SEND TO THE SERVER THE COMMAND TO EXECUTE THE CORRECT BASH FILE ---#
    if self.selected_map == 'Simple Office':
        bytes_to_send=parse_bash_file(SIMPLE_OFFICE)
        send_data(bytes_to_send)
        #update the map name into eye_blink_detector script
        update_map_name(self.selected_map)

    elif self.selected_map == "Simple Office With People":
        bytes_to_send=parse_bash_file(SIMPLE_OFFICE_WITH_PEOPLE)
        send_data(bytes_to_send)
        #update the map name into eye_blink_detector script
        update_map_name(self.selected_map)
    
    elif self.selected_map == "Real Tiago":
        bytes_to_send = parse_bash_file(REAL_TIAGO)
        send_data(bytes_to_send)


    #Sleep 20 seconds in order to give time to Ubuntu to run all topics
    time.sleep(20)

    # Create object of openCV, Reaching class and filter_butter3
    cap = cv2.VideoCapture(0)
    r = Reaching()
    r.control_arm = True
    controlling = "arm"
    update_teleoperation_state(controlling)
    filter_curs = FilterButter3("lowpass_4")

    # initialize target position
    #reaching_functions.initialize_targets(r)

    # load BoMI forward map parameters for converting body landmarks into cursor coordinates
    map = load_bomi_map(dr_mode, drPath)

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # load scaling values saved after training AE for covering entire monitor workspace
    rot = pd.read_csv(drPath + 'rotation_dr.txt', sep=' ', header=None).values
    scale = pd.read_csv(drPath + 'scale_dr.txt', sep=' ', header=None).values
    scale = np.reshape(scale, (scale.shape[0],))
    off = pd.read_csv(drPath + 'offset_dr.txt', sep=' ', header=None).values
    off = np.reshape(off, (off.shape[0],))

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    #StopWatch
    timer_enter_button = StopWatch()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 0
    opencv_thread = Thread(target=get_data_from_camera, args=(cap, q_frame, r, cal))
    opencv_thread.start()
    print("openCV thread started in customization.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                            args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in customization.")


    #Init Blinkinkg Eyes Detection
    init_blinking_detection(True,lx_threshold,rx_threshold, cap,nose_threshold)


    # Define some colors
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255,0,0)
    CURSOR = (0.19 * 255, 0.65 * 255, 0.4 * 255)
    ORANGE = (255,165,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)

    pygame.init()

    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    # Open a new window
    size = (r.base_width, r.base_height)
    screen = pygame.display.set_mode(size)

    # -------- Main Program Loop -----------
    while not r.is_terminated:
        if arm_state.get() == False:
            arm_state_teleop = True
            bytes_to_send=set_arm_teleop_state(arm_state_teleop)
            send_data(bytes_to_send)
            while arm_state.empty():
                # --- Main 2D Vector Teleoperation --- #
                for event in pygame.event.get():  # User did something
                    if event.type == pygame.QUIT:  # If user clicked close
                        r.is_terminated = True  # Flag that we are done so we exit this loop
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                            r.is_terminated = True
                        if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                            pyautogui.click(r.crs_x, r.crs_y)

                if not r.is_paused:
                    # Copy old cursor position
                    r.old_crs_x = r.crs_x
                    r.old_crs_y = r.crs_y

                    # get current value of body
                    r.body = np.copy(body)

                    # apply BoMI forward map to body vector to obtain cursor position
                    r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

                    # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                    try:
                        rot_custom = int(self.retrieve_txt_rot())
                    except:
                        rot_custom = 0
                    try:
                        gx_custom = float(self.retrieve_txt_gx())
                    except:
                        gx_custom = 1.0
                    try:
                        gy_custom = float(self.retrieve_txt_gy())
                    except:
                        gy_custom = 1.0
                    try:
                        ox_custom = int(self.retrieve_txt_ox())
                    except:
                        ox_custom = 0
                    try:
                        oy_custom = int(self.retrieve_txt_oy())
                    except:
                        oy_custom = 0

                    # Applying rotation
                    r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                    r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                    # Applying scale
                    r.crs_x = r.crs_x * gx_custom
                    r.crs_y = r.crs_y * gy_custom
                    # Applying offset
                    r.crs_x = r.crs_x + ox_custom
                    r.crs_y = r.crs_y + oy_custom

                    # Limit cursor workspace
                    if r.crs_x >= r.base_width:
                        r.crs_x = r.base_width
                    if r.crs_x <= 0:
                        r.crs_x = 0
                    if r.crs_y >= r.base_height:
                        r.crs_y = 0
                    if r.crs_y <= 0:
                        r.crs_y = r.base_height

                    # Filter the cursor
                    r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

                    # Set target position to update the GUI
                    #reaching_functions.set_target_reaching_customization(r)

                    # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
                    screen.fill(BLACK)

                    # draw cursor
                    #pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

                    # draw the vector on the 2D plane
                    pygame.draw.line(screen,RED,(900,450),(int(r.crs_x), int(r.crs_y)),width=5)

                    #draw the arrow on top of the vector
                    #if cursor in the first quadrant
                    if (int(r.crs_x) >= 900 and int(r.crs_x) <= 1800) and (int(r.crs_y)>= 0 and int(r.crs_y) <= 450): 
                        distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                        if distance == 0:
                            distance = 0.00001
                        alpha=math.asin((450-int(r.crs_y) ) / distance)
                        alpha_deg = math.degrees(alpha)
                        amplitude_arrow = compute_amplitude(alpha_deg)
                        if alpha_deg >= 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - 25, int(r.crs_y) + amplitude_arrow),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) + 25)],width=5)
                        elif alpha_deg < 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - 25, int(r.crs_y) - amplitude_arrow),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) + 25)],width=5)
                        font = pygame.font.Font('freesansbold.ttf', 35)
                        stampa = "Alpha: " + str(alpha_deg)
                        text4 = font.render(stampa,True,BLACK,GREEN)
                        textRect4 = text4.get_rect()
                        textRect4.center = (900,450)
                        screen.blit(text4,textRect4)

                    #if cursor in the second quadrant
                    elif (int(r.crs_x) >= 0 and int(r.crs_x) <= 900) and (int(r.crs_y)>= 0 and int(r.crs_y) <= 450):
                        distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                        if distance == 0:
                            distance = 0.00001
                        alpha=math.asin((450-int(r.crs_y)) / distance)
                        alpha_deg = math.degrees(alpha)
                        amplitude_arrow = compute_amplitude(alpha_deg)
                        if alpha_deg <= 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) + 25),(int(r.crs_x) +25, int(r.crs_y) - amplitude_arrow)],width=5)
                        elif alpha_deg > 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) + 25),(int(r.crs_x)  + 25, int(r.crs_y) + amplitude_arrow)],width=5)
                        font = pygame.font.Font('freesansbold.ttf', 35)
                        alpha_deg = 180 - alpha_deg
                        stampa = "Alpha: " + str(alpha_deg)
                        text4 = font.render(stampa,True,BLACK,GREEN)
                        textRect4 = text4.get_rect()
                        textRect4.center = (900,450)
                        screen.blit(text4,textRect4)

                    #if cursor in the third quadrant
                    elif (int(r.crs_x) >= 0 and int(r.crs_x) <= 900) and (int(r.crs_y) > 450 and int(r.crs_y) <= 900):
                        distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                        #Avoid division by 0
                        if distance == 0:
                            distance = 0.00001
                        alpha=math.asin((int(r.crs_y) - 450) / distance)
                        alpha_deg = math.degrees(alpha)
                        amplitude_arrow = compute_amplitude(alpha_deg)
                        if alpha_deg <= 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x) +25, int(r.crs_y) + amplitude_arrow)],width=5)
                        elif alpha_deg > 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x)  + 25, int(r.crs_y) - amplitude_arrow)],width=5)
                        font = pygame.font.Font('freesansbold.ttf', 35)
                        alpha_deg = 180 + alpha_deg
                        stampa = "Alpha: " + str(alpha_deg)
                        text4 = font.render(stampa,True,BLACK,GREEN)
                        textRect4 = text4.get_rect()
                        textRect4.center = (900,450)
                        screen.blit(text4,textRect4)

                    #if cursor in the fourth quadrant
                    else:
                        distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                        #Avoid division by 0
                        if distance == 0:
                            distance = 0.00001
                        alpha=math.asin((int(r.crs_y) - 450) / distance)
                        alpha_deg = math.degrees(alpha)
                        amplitude_arrow = compute_amplitude(alpha_deg)
                        if alpha_deg <= 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x) - 25, int(r.crs_y) + amplitude_arrow)],width=5)
                        elif alpha_deg > 45:
                            pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x)  - 25, int(r.crs_y) - amplitude_arrow)],width=5)
                        font = pygame.font.Font('freesansbold.ttf', 35)
                        alpha_deg = 360 - alpha_deg
                        stampa = "Alpha: " + str(alpha_deg)
                        text4 = font.render(stampa,True,BLACK,GREEN)
                        textRect4 = text4.get_rect()
                        textRect4.center = (900,450)
                        screen.blit(text4,textRect4)


                    #Parse the information of the vector in order to be sent
                    #Limit to integer alpha_deg and distance
                    distance = int(distance)
                    alpha_deg = int(alpha_deg)
                    update_vector(distance,alpha_deg)


                    # draw 2D Cartesian Axes
                    pygame.draw.line(screen,GREEN,(900,900),(900,0),width=3)
                    pygame.draw.line(screen,GREEN,(0,450),(1800,450),width=3)

                    #draw the arrow on top of the axes
                    pygame.draw.polygon(screen,GREEN,[(1800,450),(1775,425),(1775,475)],width=3)
                    pygame.draw.polygon(screen,GREEN,[(900,0),(875,25),(925,25)],width=3)
                    #pygame.draw.polygon(screen,GREEN,[(1800,0),(1775,0),(1800,25)],width=3)


                    # declare the font
                    font = pygame.font.Font('freesansbold.ttf', 75)
                    font2 = pygame.font.Font('freesansbold.ttf', 35)
                

                    # --- update the screen with what we've drawn.
                    pygame.display.flip()

                    # --- Limit to 50 frames per second
                    clock.tick(50)
        else:
            arm_state_teleop = False
            bytes_to_send=set_arm_teleop_state(arm_state_teleop)
            send_data(bytes_to_send)
            while arm_state.empty():
                # --- Main 2D Vector Teleoperation --- #
                for event in pygame.event.get():  # User did something
                    if event.type == pygame.QUIT:  # If user clicked close
                        r.is_terminated = True  # Flag that we are done so we exit this loop
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                            r.is_terminated = True
                        if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                            pyautogui.click(r.crs_x, r.crs_y)

                if not r.is_paused:
                    # Copy old cursor position
                    r.old_crs_x = r.crs_x
                    r.old_crs_y = r.crs_y

                    # get current value of body
                    r.body = np.copy(body)

                    # apply BoMI forward map to body vector to obtain cursor position
                    r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

                    # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                    try:
                        rot_custom = int(self.retrieve_txt_rot())
                    except:
                        rot_custom = 0
                    try:
                        gx_custom = float(self.retrieve_txt_gx())
                    except:
                        gx_custom = 1.0
                    try:
                        gy_custom = float(self.retrieve_txt_gy())
                    except:
                        gy_custom = 1.0
                    try:
                        ox_custom = int(self.retrieve_txt_ox())
                    except:
                        ox_custom = 0
                    try:
                        oy_custom = int(self.retrieve_txt_oy())
                    except:
                        oy_custom = 0

                    # Applying rotation
                    r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                    r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                    # Applying scale
                    r.crs_x = r.crs_x * gx_custom
                    r.crs_y = r.crs_y * gy_custom
                    # Applying offset
                    r.crs_x = r.crs_x + ox_custom
                    r.crs_y = r.crs_y + oy_custom

                    # Limit cursor workspace
                    if r.crs_x >= r.base_width:
                        r.crs_x = r.base_width
                    if r.crs_x <= 0:
                        r.crs_x = 0
                    if r.crs_y >= r.base_height:
                        r.crs_y = 0
                    if r.crs_y <= 0:
                        r.crs_y = r.base_height

                    # Filter the cursor
                    r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

                    # Set target position to update the GUI
                    #reaching_functions.set_target_reaching_customization(r)

                    # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
                    screen.fill(BLACK)

                    # draw 2D Cartesian Axes
                    pygame.draw.line(screen,GREEN,(900,900),(900,0),width=3)
                    pygame.draw.line(screen,GREEN,(0,450),(1800,450),width=3)

                    #draw the arrow on top of the axes
                    pygame.draw.polygon(screen,GREEN,[(1800,450),(1775,425),(1775,475)],width=3)
                    pygame.draw.polygon(screen,GREEN,[(900,0),(875,25),(925,25)],width=3)
                    #pygame.draw.polygon(screen,GREEN,[(1800,0),(1775,0),(1800,25)],width=3)

                    if r.crs_y < 450:
                        #draw the vector in RED and its arrow
                        pygame.draw.line(screen,RED,(900,r.crs_y),(900,450),width=5)
                        pygame.draw.polygon(screen,RED,[(900,r.crs_y),(875,r.crs_y+25),(925,r.crs_y+25)],width=5)
                        distance = 450 - r.crs_y
                        alpha_deg = 90

                    elif r.crs_y > 450:
                        #draw the vector in RED and its arrow
                        pygame.draw.line(screen,RED,(900,r.crs_y),(900,450),width=5)
                        pygame.draw.polygon(screen,RED,[(900,r.crs_y),(875,r.crs_y-25),(925,r.crs_y-25)],width=5)
                        distance = r.crs_y - 450
                        alpha_deg = 270

                    elif r.crs_y == 450:
                        distance = 0
                        alpha_deg = 90


                    #Limit to integer alpha_deg and distance
                    distance = int(distance)
                    
                    #Update vector information in order to send it into eye detector script
                    update_vector(distance,alpha_deg)


                    # --- update the screen with what we've drawn.
                    pygame.display.flip()

                    # --- Limit to 50 frames per second
                    clock.tick(50)
                
                        
    # Once we have exited the main program loop, stop the game engine and release the capture
    r.control_arm = False
    controlling = ""
    update_teleoperation_state(controlling)
    pygame.quit()
    print("game engine object released in customization.")
    holistic.close()
    print("pose estimation object released terminated in customization.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in customization.")


    # Once we have exited the main program loop, stop the game engine and release the capture
    pygame.quit()
    print("game engine object released in customization.")
    holistic.close()
    print("pose estimation object released terminated in customization.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in customization.")

    

def initialize_free_mode(self, dr_mode, drPath, num_joints, joints):
    """
    Function callback of the button free mode practice
    This function mix the base teleoperation functionality
    with the arm teleoperation functionality.
    In particular the switch mode between the two functionalities
    is firex pressing the c keyboard button
    :param self: CustomizationApplication tkinter Frame. needed to retrieve textbox values programmatically
    :param drPath: path to load the BoMI forward map
    :param num_joints: the number of joints used to teleoperate TIAgo
    :param joints: type of joints used to teleoperate TIAGo
    """
    global holistic,cap, base_state_teleop,controlling,nose_threshold,fsm_state

    # --- SEND TO THE SERVER THE COMMAND TO EXECUTE THE CORRECT BASH FILE ---#
    if self.selected_map == 'Simple Office':
        bytes_to_send=parse_bash_file(SIMPLE_OFFICE)
        send_data(bytes_to_send)
        #update the map name into eye_blink_detector script
        update_map_name(self.selected_map)

    elif self.selected_map == "Simple Office With People":
        bytes_to_send=parse_bash_file(SIMPLE_OFFICE_WITH_PEOPLE)
        send_data(bytes_to_send)
        #update the map name into eye_blink_detector script
        update_map_name(self.selected_map)
    
    elif self.selected_map == "Real Tiago":
        bytes_to_send = parse_bash_file(REAL_TIAGO)
        send_data(bytes_to_send)

    #Sleep 20 seconds in order to give time to Ubuntu to run all topics
    time.sleep(20)

    # Create object of openCV, Reaching class and filter_butter3
    cap = cv2.VideoCapture(0)
    r = Reaching()

    filter_curs = FilterButter3("lowpass_4")

    # initialize target position
    #reaching_functions.initialize_targets(r)

    # load BoMI forward map parameters for converting body landmarks into cursor coordinates
    map = load_bomi_map(dr_mode, drPath)

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # load scaling values saved after training AE for covering entire monitor workspace
    rot = pd.read_csv(drPath + 'rotation_dr.txt', sep=' ', header=None).values
    scale = pd.read_csv(drPath + 'scale_dr.txt', sep=' ', header=None).values
    scale = np.reshape(scale, (scale.shape[0],))
    off = pd.read_csv(drPath + 'offset_dr.txt', sep=' ', header=None).values
    off = np.reshape(off, (off.shape[0],))

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 0
    opencv_thread = Thread(target=get_data_from_camera, args=(cap, q_frame, r, cal))
    opencv_thread.start()
    print("openCV thread started in customization.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                              args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in customization.")

    #Init Blinkinkg Eyes Detection
    init_blinking_detection(True,lx_threshold,rx_threshold, cap,nose_threshold)

    # Define some colors
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255,0,0)
    CURSOR = (0.19 * 255, 0.65 * 255, 0.4 * 255)
    WHITE = (255,255,255)

    #Define variables to create 'odom' GUI
    point_on_x_axis = np.linspace(0,1800,21)
    point_on_y_axis = np.linspace(0,900,15)

    neg_index = 10  
    pos_index = 1

    pygame.init()

    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    #Initialize stopwatch to control velocity selection
    timer_enter_region = StopWatch()

    # Open a new window
    size = (r.base_width, r.base_height)
    screen = pygame.display.set_mode(size)

    # Variable to store base and arm state
    # If free_mode == False --> Teleoperate Base
    # If free_mode == True --> Teleoperate Arm
    free_mode  = False

    # -- Start from Nine Regions GUI -- #
    # if base_state_var == False --> Nine Regions
    # if base_state_var == True --> Odom GUI
    base_state_var = False

    # -- Start from 3D Vector GUI -- #
    # if arm_state_var == False --> 2D Vector GUI
    # if arm_state_var == True --> 1D Vector GUI
    arm_state_var = False

    # -- In order to send base information one time -- #
    published_nine_regions = False
    published_odom = False
    published_2D_vector = False
    published_1D_vector = False

    # -- Variable to store the state of the button c -- #
    state_button = "None"
    
    # -------- Main Program Loop -----------##
    while not r.is_terminated:
        if not fsm_state.empty():
            free_mode = fsm_state.get()
        if free_mode == False:
            controlling = "base"
            update_teleoperation_state(controlling)
            r.control_base = True
            r.control_arm = False
            state_button = "None"
            while free_mode == False:
                if not fsm_state.empty():
                    free_mode=fsm_state.get()

                # -- Nine Regions GUI -- #
                while base_state_var == False and fsm_state.empty() and free_mode == False: #state_button == "None":
                    if not base_state.empty():
                        base_state_var = base_state.get()
                        published_nine_regions = False
                    if published_nine_regions == False:
                        base_state_teleop = True
                        bytes_to_send=set_base_teleop_state(base_state_teleop)
                        send_data(bytes_to_send)
                        published_nine_regions = True
                        published_odom = False
                        published_2D_vector = False
                        published_1D_vector = False

                    # --- Main Nine Regions GUI -- #
                    for event in pygame.event.get():  # User did something
                        if event.type == pygame.QUIT:  # If user clicked close
                            r.is_terminated = True  # Flag that we are done so we exit this loop
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                                r.is_terminated = True
                            if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                                pyautogui.click(r.crs_x, r.crs_y)
                            if event.key == pygame.K_c: #pressing the c key will change teleoperation state
                                free_mode = not free_mode
                                state_button = "Pressed"

                    if not r.is_paused:
                        # Copy old cursor position
                        r.old_crs_x = r.crs_x
                        r.old_crs_y = r.crs_y

                        # get current value of body
                        r.body = np.copy(body)

                        # apply BoMI forward map to body vector to obtain cursor position
                        r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)


                        # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                        try:
                            rot_custom = int(self.retrieve_txt_rot())
                        except:
                            rot_custom = 0
                        try:
                            gx_custom = float(self.retrieve_txt_gx())
                        except:
                            gx_custom = 1.0
                        try:
                            gy_custom = float(self.retrieve_txt_gy())
                        except:
                            gy_custom = 1.0
                        try:
                            ox_custom = int(self.retrieve_txt_ox())
                        except:
                            ox_custom = 0
                        try:
                            oy_custom = int(self.retrieve_txt_oy())
                        except:
                            oy_custom = 0

                        # Applying rotation
                        r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                        r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                        # Applying scale
                        r.crs_x = r.crs_x * gx_custom
                        r.crs_y = r.crs_y * gy_custom
                        # Applying offset
                        r.crs_x = r.crs_x + ox_custom
                        r.crs_y = r.crs_y + oy_custom

                        # Limit cursor workspace
                        if r.crs_x >= r.base_width:
                            r.crs_x = r.base_width
                        if r.crs_x <= 0:
                            r.crs_x = 0
                        if r.crs_y >= r.base_height:
                            r.crs_y = 0
                        if r.crs_y <= 0:
                            r.crs_y = r.base_height

                        # Filter the cursor
                        r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

                        # Set target position to update the GUI
                        #reaching_functions.set_target_reaching_customization(r)

                        # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
                        screen.fill(BLACK)

                        # draw cursor
                        pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

                        # draw each separetor bar
                        pygame.draw.rect(screen,GREEN,pygame.Rect(600,0,5,900))
                        pygame.draw.rect(screen,GREEN,pygame.Rect(1200,0,5,900))
                        pygame.draw.rect(screen,GREEN,pygame.Rect(0,300,1800,5))
                        pygame.draw.rect(screen,GREEN,pygame.Rect(0,600,1800,5))
                    
                        

                        # --- update region position 
                        reaching_functions.check_region_cursor(r,timer_enter_region)

                        #-- check stopwatch and compute velocities
                        reaching_functions.check_time_region(r,timer_enter_region)

                        #Log schermo
                        font = pygame.font.Font('freesansbold.ttf', 35)
                        stampa = "Lin Vel: " + str(r.lin_vel) + " Ang vel: " + str(r.ang_vel)
                        text4 = font.render(stampa,True,BLACK,GREEN)
                        textRect4 = text4.get_rect()
                        textRect4.center = (900,450)
                        screen.blit(text4,textRect4)



                        #parse the string to be send
                        bytes_string = parse_velocities(r)
                        send_data(bytes_string)

                        # --- update the screen with what we've drawn.
                        pygame.display.flip()

                        # --- Limit to 50 frames per second
                        clock.tick(50)

                if not fsm_state.empty():
                    free_mode = fsm_state.get()

                # -- Odom GUI -- #
                while base_state_var == True and fsm_state.empty() and free_mode==False: #state_button == "None":
                    if not base_state.empty():
                        base_state_var = base_state.get() 
                        published_odom = False
                    if published_odom == False:
                        base_state_teleop = False
                        bytes_to_send=set_base_teleop_state(base_state_teleop)
                        send_data(bytes_to_send)
                        published_odom = True
                        published_nine_regions = False
                        published_2D_vector = False
                        published_1D_vector = False
                    # --- Main event loop Odom GUI ---#
                    for event in pygame.event.get():  # User did something
                        if event.type == pygame.QUIT:  # If user clicked close
                            r.is_terminated = True  # Flag that we are done so we exit this loop
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                                r.is_terminated = True
                            if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                                pyautogui.click(r.crs_x, r.crs_y)
                            if event.key == pygame.K_c: #pressing the c key will change teleoperation state
                                free_mode = not free_mode
                                state_button = "Pressed"

                    if not r.is_paused:
                        # Copy old cursor position
                        r.old_crs_x = r.crs_x
                        r.old_crs_y = r.crs_y

                        # get current value of body
                        r.body = np.copy(body)

                        # apply BoMI forward map to body vector to obtain cursor position
                        r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

                        # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                        try:
                            rot_custom = int(self.retrieve_txt_rot())
                        except:
                            rot_custom = 0
                        try:
                            gx_custom = float(self.retrieve_txt_gx())
                        except:
                            gx_custom = 1.0
                        try:
                            gy_custom = float(self.retrieve_txt_gy())
                        except:
                            gy_custom = 1.0
                        try:
                            ox_custom = int(self.retrieve_txt_ox())
                        except:
                            ox_custom = 0
                        try:
                            oy_custom = int(self.retrieve_txt_oy())
                        except:
                            oy_custom = 0

                        # Applying rotation
                        r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                        r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                        # Applying scale
                        r.crs_x = r.crs_x * gx_custom
                        r.crs_y = r.crs_y * gy_custom
                        # Applying offset
                        r.crs_x = r.crs_x + ox_custom
                        r.crs_y = r.crs_y + oy_custom

                        # Limit cursor workspace
                        if r.crs_x >= r.base_width:
                            r.crs_x = r.base_width
                        if r.crs_x <= 0:
                            r.crs_x = 0
                        if r.crs_y >= r.base_height:
                            r.crs_y = 0
                        if r.crs_y <= 0:
                            r.crs_y = r.base_height

                        # Filter the cursor
                        r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)
                        update_mouse_coordinates(r)
                        

                        # Set target position to update the GUI
                        #reaching_functions.set_target_reaching_customization(r)

                        # First, clear the screen to white. In between screen.fill and pygame.display.flip() all the draw
                        screen.fill(WHITE)

                        # draw cursor
                        pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

                        neg_index = 10  
                        pos_index = 1

                        #draw numbers on the x-axis
                        font = pygame.font.Font('freesansbold.ttf', 20)
                        for x_coordinate in point_on_x_axis:
                            if x_coordinate < 900:
                                text = font.render( '-' + str(neg_index),True,BLACK,WHITE)
                                textRect = text.get_rect()
                                textRect.center = (x_coordinate,490)
                                screen.blit(text,textRect)
                                neg_index -= 1
                            if x_coordinate > 900:
                                text = font.render(str(pos_index),True,BLACK,WHITE)
                                textRect = text.get_rect()
                                textRect.center = (x_coordinate,490)
                                screen.blit(text,textRect)
                                pos_index += 1

                        pos_index = 7
                        neg_index = 1


                        #draw nubers on the y-axis
                        for y_coordinate in point_on_y_axis:
                            if y_coordinate > 500:
                                text = font.render( '-' + str(neg_index),True,BLACK,WHITE)
                                textRect = text.get_rect()
                                textRect.center = (930,y_coordinate)
                                screen.blit(text,textRect)
                                neg_index += 1
                            if y_coordinate < 450:
                                text = font.render(str(pos_index),True,BLACK,WHITE)
                                textRect = text.get_rect()
                                textRect.center = (930,y_coordinate)
                                screen.blit(text,textRect)
                                pos_index -= 1
                        

                        pygame.draw.rect(screen,BLACK,pygame.Rect(900,0,5,900))
                        pygame.draw.rect(screen,BLACK,pygame.Rect(0,450,1800,5))
            
                        # draw segment on x and y axes
                        for x_coordinate in point_on_x_axis:
                            pygame.draw.rect(screen,BLACK,pygame.Rect(x_coordinate,443,5,20))
                
                        for y_coordinate in point_on_y_axis:
                            pygame.draw.rect(screen,BLACK,pygame.Rect(893,y_coordinate,20,5))

                        # --- update the screen with what we've drawn.
                        pygame.display.flip()

                        # --- Limit to 50 frames per second
                        clock.tick(50)

                if not fsm_state.empty():
                    free_mode = fsm_state.get()

        else:
            r.control_arm = True
            r.control_base = False
            controlling = "arm"
            update_teleoperation_state(controlling)
            state_button = "None"
            while free_mode == True:
                
                if not fsm_state.empty():
                    free_mode = fsm_state.get()

                # -- 2D Vector GUI -- #
                while arm_state_var == False and fsm_state.empty() and free_mode == True: #state_button == "None":
                    if not arm_state.empty():
                        arm_state_var = arm_state.get()
                        published_2D_vector = False
                    if published_2D_vector== False:
                        arm_state_teleop = True
                        bytes_to_send=set_arm_teleop_state(arm_state_teleop)
                        send_data(bytes_to_send)
                        published_2D_vector = True
                        published_1D_vector = False
                        published_nine_regions = False
                        published_odom = False
                    
                    # --- Main 2D Vector Teleoperation --- #
                    for event in pygame.event.get():  # User did something
                        if event.type == pygame.QUIT:  # If user clicked close
                            r.is_terminated = True  # Flag that we are done so we exit this loop
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                                r.is_terminated = True
                            if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                                pyautogui.click(r.crs_x, r.crs_y)
                            if event.key == pygame.K_c: #pressing the c key will change teleoperation state
                                free_mode = not free_mode
                                state_button = "Pressed"
                    
                    if not r.is_paused:
                        # Copy old cursor position
                        r.old_crs_x = r.crs_x
                        r.old_crs_y = r.crs_y

                        # get current value of body
                        r.body = np.copy(body)

                        # apply BoMI forward map to body vector to obtain cursor position
                        r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

                        # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                        try:
                            rot_custom = int(self.retrieve_txt_rot())
                        except:
                            rot_custom = 0
                        try:
                            gx_custom = float(self.retrieve_txt_gx())
                        except:
                            gx_custom = 1.0
                        try:
                            gy_custom = float(self.retrieve_txt_gy())
                        except:
                            gy_custom = 1.0
                        try:
                            ox_custom = int(self.retrieve_txt_ox())
                        except:
                            ox_custom = 0
                        try:
                            oy_custom = int(self.retrieve_txt_oy())
                        except:
                            oy_custom = 0

                        # Applying rotation
                        r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                        r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                        # Applying scale
                        r.crs_x = r.crs_x * gx_custom
                        r.crs_y = r.crs_y * gy_custom
                        # Applying offset
                        r.crs_x = r.crs_x + ox_custom
                        r.crs_y = r.crs_y + oy_custom

                        # Limit cursor workspace
                        if r.crs_x >= r.base_width:
                            r.crs_x = r.base_width
                        if r.crs_x <= 0:
                            r.crs_x = 0
                        if r.crs_y >= r.base_height:
                            r.crs_y = 0
                        if r.crs_y <= 0:
                            r.crs_y = r.base_height

                        # Filter the cursor
                        r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

                        # Set target position to update the GUI
                        #reaching_functions.set_target_reaching_customization(r)

                        # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
                        screen.fill(BLACK)

                        # draw cursor
                        #pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

                        # draw the vector on the 2D plane
                        pygame.draw.line(screen,RED,(900,450),(int(r.crs_x), int(r.crs_y)),width=5)

                        #draw the arrow on top of the vector
                        #if cursor in the first quadrant
                        if (int(r.crs_x) >= 900 and int(r.crs_x) <= 1800) and (int(r.crs_y)>= 0 and int(r.crs_y) <= 450): 
                            distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                            if distance == 0:
                                distance = 0.00001
                            alpha=math.asin((450-int(r.crs_y) ) / distance)
                            alpha_deg = math.degrees(alpha)
                            amplitude_arrow = compute_amplitude(alpha_deg)
                            if alpha_deg >= 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - 25, int(r.crs_y) + amplitude_arrow),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) + 25)],width=5)
                            elif alpha_deg < 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - 25, int(r.crs_y) - amplitude_arrow),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) + 25)],width=5)
                            font = pygame.font.Font('freesansbold.ttf', 35)
                            stampa = "Alpha: " + str(alpha_deg)
                            text4 = font.render(stampa,True,BLACK,GREEN)
                            textRect4 = text4.get_rect()
                            textRect4.center = (900,450)
                            screen.blit(text4,textRect4)

                        #if cursor in the second quadrant
                        elif (int(r.crs_x) >= 0 and int(r.crs_x) <= 900) and (int(r.crs_y)>= 0 and int(r.crs_y) <= 450):
                            distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                            if distance == 0:
                                distance = 0.00001
                            alpha=math.asin((450-int(r.crs_y)) / distance)
                            alpha_deg = math.degrees(alpha)
                            amplitude_arrow = compute_amplitude(alpha_deg)
                            if alpha_deg <= 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) + 25),(int(r.crs_x) +25, int(r.crs_y) - amplitude_arrow)],width=5)
                            elif alpha_deg > 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) + 25),(int(r.crs_x)  + 25, int(r.crs_y) + amplitude_arrow)],width=5)
                            font = pygame.font.Font('freesansbold.ttf', 35)
                            alpha_deg = 180 - alpha_deg
                            stampa = "Alpha: " + str(alpha_deg)
                            text4 = font.render(stampa,True,BLACK,GREEN)
                            textRect4 = text4.get_rect()
                            textRect4.center = (900,450)
                            screen.blit(text4,textRect4)

                        #if cursor in the third quadrant
                        elif (int(r.crs_x) >= 0 and int(r.crs_x) <= 900) and (int(r.crs_y) > 450 and int(r.crs_y) <= 900):
                            distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                            #Avoid division by 0
                            if distance == 0:
                                distance = 0.00001
                            alpha=math.asin((int(r.crs_y) - 450) / distance)
                            alpha_deg = math.degrees(alpha)
                            amplitude_arrow = compute_amplitude(alpha_deg)
                            if alpha_deg <= 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x) +25, int(r.crs_y) + amplitude_arrow)],width=5)
                            elif alpha_deg > 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x)  + 25, int(r.crs_y) - amplitude_arrow)],width=5)
                            font = pygame.font.Font('freesansbold.ttf', 35)
                            alpha_deg = 180 + alpha_deg
                            stampa = "Alpha: " + str(alpha_deg)
                            text4 = font.render(stampa,True,BLACK,GREEN)
                            textRect4 = text4.get_rect()
                            textRect4.center = (900,450)
                            screen.blit(text4,textRect4)

                        #if cursor in the fourth quadrant
                        else:
                            distance = euclidian_distance(int(r.crs_x),int(r.crs_y))
                            #Avoid division by 0
                            if distance == 0:
                                distance = 0.00001
                            alpha=math.asin((int(r.crs_y) - 450) / distance)
                            alpha_deg = math.degrees(alpha)
                            amplitude_arrow = compute_amplitude(alpha_deg)
                            if alpha_deg <= 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) - amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x) - 25, int(r.crs_y) + amplitude_arrow)],width=5)
                            elif alpha_deg > 45:
                                pygame.draw.polygon(screen,RED,[(int(r.crs_x), int(r.crs_y)),(int(r.crs_x) + amplitude_arrow, int(r.crs_y) - 25),(int(r.crs_x)  - 25, int(r.crs_y) - amplitude_arrow)],width=5)
                            font = pygame.font.Font('freesansbold.ttf', 35)
                            alpha_deg = 360 - alpha_deg
                            stampa = "Alpha: " + str(alpha_deg)
                            text4 = font.render(stampa,True,BLACK,GREEN)
                            textRect4 = text4.get_rect()
                            textRect4.center = (900,450)
                            screen.blit(text4,textRect4)


                        #Parse the information of the vector in order to be sent
                        #Limit to integer alpha_deg and distance
                        distance = int(distance)
                        alpha_deg = int(alpha_deg)
                        update_vector(distance,alpha_deg)


                        # draw 2D Cartesian Axes
                        pygame.draw.line(screen,GREEN,(900,900),(900,0),width=3)
                        pygame.draw.line(screen,GREEN,(0,450),(1800,450),width=3)

                        #draw the arrow on top of the axes
                        pygame.draw.polygon(screen,GREEN,[(1800,450),(1775,425),(1775,475)],width=3)
                        pygame.draw.polygon(screen,GREEN,[(900,0),(875,25),(925,25)],width=3)
                        #pygame.draw.polygon(screen,GREEN,[(1800,0),(1775,0),(1800,25)],width=3)


                        # declare the font
                        font = pygame.font.Font('freesansbold.ttf', 75)
                        font2 = pygame.font.Font('freesansbold.ttf', 35)
                    

                        # --- update the screen with what we've drawn.
                        pygame.display.flip()

                        # --- Limit to 50 frames per second
                        clock.tick(50)
                
                if not fsm_state.empty():
                    free_mode = fsm_state.get()

                # -- 1D Vector GUI -- #
                while arm_state_var == True and fsm_state.empty() and free_mode == True: #state_button == "None":
                    if not arm_state.empty():
                        arm_state_var = arm_state.get()
                        published_1D_vector = False
                    if published_1D_vector== False:
                        arm_state_teleop = False
                        bytes_to_send=set_arm_teleop_state(arm_state_teleop)
                        send_data(bytes_to_send)
                        published_1D_vector = True
                        published_2D_vector = False
                        published_nine_regions = False
                        published_odom = False
                    
                    # --- Main 1D Vector Teleoperation --- #
                    for event in pygame.event.get():  # User did something
                        if event.type == pygame.QUIT:  # If user clicked close
                            r.is_terminated = True  # Flag that we are done so we exit this loop
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                                r.is_terminated = True
                            if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                                pyautogui.click(r.crs_x, r.crs_y)
                            if event.key == pygame.K_c: #pressing the c key will change teleoperation state
                                free_mode = not free_mode
                                state_button = "Pressed"
    
                    if not r.is_paused:
                        # Copy old cursor position
                        r.old_crs_x = r.crs_x
                        r.old_crs_y = r.crs_y

                        # get current value of body
                        r.body = np.copy(body)

                        # apply BoMI forward map to body vector to obtain cursor position
                        r.crs_x, r.crs_y = reaching_functions.update_cursor_position_custom(r.body, map, rot, scale, off)

                        # Apply extra customization according to textbox values (try/except allows to catch invalid inputs)
                        try:
                            rot_custom = int(self.retrieve_txt_rot())
                        except:
                            rot_custom = 0
                        try:
                            gx_custom = float(self.retrieve_txt_gx())
                        except:
                            gx_custom = 1.0
                        try:
                            gy_custom = float(self.retrieve_txt_gy())
                        except:
                            gy_custom = 1.0
                        try:
                            ox_custom = int(self.retrieve_txt_ox())
                        except:
                            ox_custom = 0
                        try:
                            oy_custom = int(self.retrieve_txt_oy())
                        except:
                            oy_custom = 0

                        # Applying rotation
                        r.crs_x = r.crs_x * np.cos(np.pi / 180 * rot_custom) - r.crs_y * np.sin(np.pi / 180 * rot_custom)
                        r.crs_y = r.crs_x * np.sin(np.pi / 180 * rot_custom) + r.crs_y * np.cos(np.pi / 180 * rot_custom)
                        # Applying scale
                        r.crs_x = r.crs_x * gx_custom
                        r.crs_y = r.crs_y * gy_custom
                        # Applying offset
                        r.crs_x = r.crs_x + ox_custom
                        r.crs_y = r.crs_y + oy_custom

                        # Limit cursor workspace
                        if r.crs_x >= r.base_width:
                            r.crs_x = r.base_width
                        if r.crs_x <= 0:
                            r.crs_x = 0
                        if r.crs_y >= r.base_height:
                            r.crs_y = 0
                        if r.crs_y <= 0:
                            r.crs_y = r.base_height

                        # Filter the cursor
                        r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

                        # Set target position to update the GUI
                        #reaching_functions.set_target_reaching_customization(r)

                        # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
                        screen.fill(BLACK)

                        # draw 2D Cartesian Axes
                        pygame.draw.line(screen,GREEN,(900,900),(900,0),width=3)
                        pygame.draw.line(screen,GREEN,(0,450),(1800,450),width=3)

                        #draw the arrow on top of the axes
                        pygame.draw.polygon(screen,GREEN,[(1800,450),(1775,425),(1775,475)],width=3)
                        pygame.draw.polygon(screen,GREEN,[(900,0),(875,25),(925,25)],width=3)
                        #pygame.draw.polygon(screen,GREEN,[(1800,0),(1775,0),(1800,25)],width=3)

                        if r.crs_y < 450:
                            #draw the vector in RED and its arrow
                            pygame.draw.line(screen,RED,(900,r.crs_y),(900,450),width=5)
                            pygame.draw.polygon(screen,RED,[(900,r.crs_y),(875,r.crs_y+25),(925,r.crs_y+25)],width=5)
                            distance = 450 - r.crs_y
                            alpha_deg = 90

                        elif r.crs_y > 450:
                            #draw the vector in RED and its arrow
                            pygame.draw.line(screen,RED,(900,r.crs_y),(900,450),width=5)
                            pygame.draw.polygon(screen,RED,[(900,r.crs_y),(875,r.crs_y-25),(925,r.crs_y-25)],width=5)
                            distance = r.crs_y - 450
                            alpha_deg = 270

                        elif r.crs_y == 450:
                            distance = 0
                            alpha_deg = 90


                        #Limit to integer alpha_deg and distance
                        distance = int(distance)
                        
                        #Update vector information in order to send it into eye detector script
                        update_vector(distance,alpha_deg)


                        # --- update the screen with what we've drawn.
                        pygame.display.flip()

                        # --- Limit to 50 frames per second
                        clock.tick(50)

                if not fsm_state.empty():
                    free_mode = fsm_state.get()

    # Once we have exited the main program loop, stop the game engine and release the capture
    r.control_base = False
    r.control_arm = False
    controlling = ""
    update_teleoperation_state(controlling)
    pygame.quit()
    print("game engine object released in customization.")
    holistic.close()
    print("pose estimation object released terminated in customization.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in customization.")

    # #///////////CLOSE SOCKET COMMUNICATION////////#
    manage_connection_server(False)
def save_parameters(self, drPath):
    """
    function to save customization values
    :param self: CustomizationApplication tkinter Frame. needed to retrieve textbox values programmatically
    :param drPath: path where to load the BoMI forward map
    :return:
    """
    # retrieve values stored in the textbox
    rot = int(self.retrieve_txt_rot())
    gx_custom = float(self.retrieve_txt_gx())
    gy_custom = float(self.retrieve_txt_gy())
    scale = [gx_custom, gy_custom]
    ox_custom = int(self.retrieve_txt_ox())
    oy_custom = int(self.retrieve_txt_oy())
    off = [ox_custom, oy_custom]

    # save customization values
    with open(drPath + "rotation_custom.txt", 'w') as f:
        print(rot, file=f)
    np.savetxt(drPath + "scale_custom.txt", scale)
    np.savetxt(drPath + "offset_custom.txt", off)

    print('Customization values have been saved. You can continue with practice.')

# [ADD CODE HERE: check_mouse as function input]
def start_reaching(drPath, lbl_tgt, num_joints, joints, dr_mode):
    """
    function to perform online cursor control - practice
    :param drPath: path where to load the BoMI forward map and customization values
    :param check_mouse: tkinter Boolean value that triggers mouse control instead of reaching task
    :param lbl_tgt: label in the main window that shows number of targets remaining
    :return:
    """
    pygame.init()

    # [ADD CODE HERE] get value from checkbox - is mouse enabled? !!!!!!!!!!!!!!!!!!!

    ############################################################

    # Define some colors
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    CURSOR = (0.19 * 255, 0.65 * 255, 0.4 * 255)

    # Create object of openCV, Reaching class and filter_butter3
    cap = cv2.VideoCapture(0)
    r = Reaching()
    filter_curs = FilterButter3("lowpass_4")

    # Open a new window
    size = (r.width, r.height)
    screen = pygame.display.set_mode(size)
    # screen = pygame.display.toggle_fullscreen()

    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    # Initialize stopwatch for counting time elapsed in the different states of the reaching
    timer_enter_tgt = StopWatch()
    timer_start_trial = StopWatch()
    timer_practice = StopWatch()

    # initialize targets and the reaching log file header
    reaching_functions.initialize_targets(r)
    reaching_functions.write_header(r)

    # load BoMI forward map parameters for converting body landmarks into cursor coordinates
    map = load_bomi_map(dr_mode, drPath)

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # load scaling values for covering entire monitor workspace
    rot_dr = pd.read_csv(drPath + 'rotation_dr.txt', sep=' ', header=None).values
    scale_dr = pd.read_csv(drPath + 'scale_dr.txt', sep=' ', header=None).values
    scale_dr = np.reshape(scale_dr, (scale_dr.shape[0],))
    off_dr = pd.read_csv(drPath + 'offset_dr.txt', sep=' ', header=None).values
    off_dr = np.reshape(off_dr, (off_dr.shape[0],))
    rot_custom = pd.read_csv(drPath + 'rotation_custom.txt', sep=' ', header=None).values
    scale_custom = pd.read_csv(drPath + 'scale_custom.txt', sep=' ', header=None).values
    scale_custom = np.reshape(scale_custom, (scale_custom.shape[0],))
    off_custom = pd.read_csv(drPath + 'offset_custom.txt', sep=' ', header=None).values
    off_custom = np.reshape(off_custom, (off_custom.shape[0],))

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 0
    opencv_thread = Thread(target=get_data_from_camera, args=(cap, q_frame, r, cal))
    opencv_thread.start()
    print("openCV thread started in practice.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                              args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in practice.")

    # initialize thread for writing reaching log file
    wfile_thread = Thread(target=write_practice_files, args=(r, timer_practice))
    timer_practice.start()  # start the timer for PracticeLog
    wfile_thread.start()
    print("writing reaching log file thread started in practice.")

    print("cursor control thread is about to start...")

    # -------- Main Program Loop -----------
    while not r.is_terminated:
        # --- Main event loop
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                r.is_terminated = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                    r.is_terminated = True
                if event.key == pygame.K_p:  # Pressing the p Key will pause/resume the game
                    reaching_functions.pause_acquisition(r, timer_practice)
                if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                    pyautogui.click(r.crs_x, r.crs_y)

        if not r.is_paused:
            # Copy old cursor position
            r.old_crs_x = r.crs_x
            r.old_crs_y = r.crs_y

            # get current value of body
            r.body = np.copy(body)

            # apply BoMI forward map to body vector to obtain cursor position.
            r.crs_x, r.crs_y = reaching_functions.update_cursor_position \
                (r.body, map, rot_dr, scale_dr, off_dr, rot_custom, scale_custom, off_custom)

            # Check if the crs is bouncing against any of the 4 walls:
            if r.crs_x >= r.width:
                r.crs_x = r.width
            if r.crs_x <= 0:
                r.crs_x = 0
            if r.crs_y >= r.height:
                r.crs_y = 0
            if r.crs_y <= 0:
                r.crs_y = r.height

            # Filter the cursor
            r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

            # if mouse checkbox was enabled do not draw the reaching GUI,
            # only change coordinates of the computer cursor !!!!!!!!!!!!!!!!!!!!!
            # [ADD CODE HERE] !!!!!!!!!!!!!!!!!!!!!


            # else: do the reaching

            # Set target position to update the GUI
            reaching_functions.set_target_reaching(r)
            # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
            screen.fill(BLACK)
            # Do not show the cursor in the blind trials when the cursor is outside the home target
            if not r.is_blind:
                # draw cursor
                pygame.draw.circle(screen, CURSOR, (int(r.crs_x), int(r.crs_y)), r.crs_radius)

            # draw target. green if blind, state 0 or 1. yellow if notBlind and state 2
            if r.state == 0:  # green
                pygame.draw.circle(screen, GREEN, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)
            elif r.state == 1:
                pygame.draw.circle(screen, GREEN, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)
            elif r.state == 2:  # yellow
                if r.is_blind:  # green again if blind trial
                    pygame.draw.circle(screen, GREEN, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)
                else:  # yellow if not blind
                    pygame.draw.circle(screen, YELLOW, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)

            # Display scores:
            font = pygame.font.Font(None, 80)
            text = font.render(str(r.score), True, RED)
            screen.blit(text, (1250, 10))

            # --- update the screen with what we've drawn.
            pygame.display.flip()

            # After showing the cursor, check whether cursor is in the target
            reaching_functions.check_target_reaching(r, timer_enter_tgt)
            # Then check if cursor stayed in the target for enough time
            reaching_functions.check_time_reaching(r, timer_enter_tgt, timer_start_trial, timer_practice)

            # update label with number of targets remaining
            tgt_remaining = 248 - r.trial + 1
            lbl_tgt.configure(text='Remaining targets: ' + str(tgt_remaining))
            lbl_tgt.update()

            # --- Limit to 50 frames per second
            clock.tick(50)

    # Once we have exited the main program loop, stop the game engine and release the capture
    pygame.quit()
    print("game engine object released in practice.")
    # pose.close()
    holistic.close()
    print("pose estimation object released in practice.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in practice.")

def start_3D_reaching(drPath, lbl_tgt, num_joints, joints, dr_mode):
    """
    function to perform 3D online cursor control - practice
    :param drPath: path where to load the BoMI forward map and customization values
    :param check_mouse: tkinter Boolean value that triggers mouse control instead of reaching task
    :param lbl_tgt: label in the main window that shows number of targets remaining
    :return:
    """
    pygame.init()

    # [ADD CODE HERE] get value from checkbox - is mouse enabled? !!!!!!!!!!!!!!!!!!!

    ############################################################

    # Define some colors
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    CURSOR = (0.19 * 255, 0.65 * 255, 0.4 * 255)

    # Create object of openCV, Reaching class and filter_butter3
    cap = cv2.VideoCapture(0)
    r = Reaching()
    filter_curs = FilterButter3("lowpass_4")

    # Open a new window
    size = (r.width, r.height)
    screen = pygame.display.set_mode(size)
    # screen = pygame.display.toggle_fullscreen()

    # The clock will be used to control how fast the screen updates
    clock = pygame.time.Clock()

    # Initialize stopwatch for counting time elapsed in the different states of the reaching
    timer_enter_tgt = StopWatch()
    timer_start_trial = StopWatch()
    timer_practice = StopWatch()

    # initialize targets and the reaching log file header
    reaching_functions.initialize_targets(r)
    reaching_functions.write_header(r)

    # load BoMI forward map parameters for converting body landmarks into cursor coordinates
    map = load_bomi_map(dr_mode, drPath)

    # initialize MediaPipe Pose
    mp_holistic = mp.solutions.holistic
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                    smooth_landmarks=False)

    # load scaling values for covering entire monitor workspace
    rot_dr = pd.read_csv(drPath + 'rotation_dr.txt', sep=' ', header=None).values
    scale_dr = pd.read_csv(drPath + 'scale_dr.txt', sep=' ', header=None).values
    scale_dr = np.reshape(scale_dr, (scale_dr.shape[0],))
    off_dr = pd.read_csv(drPath + 'offset_dr.txt', sep=' ', header=None).values
    off_dr = np.reshape(off_dr, (off_dr.shape[0],))
    rot_custom = pd.read_csv(drPath + 'rotation_custom.txt', sep=' ', header=None).values
    scale_custom = pd.read_csv(drPath + 'scale_custom.txt', sep=' ', header=None).values
    scale_custom = np.reshape(scale_custom, (scale_custom.shape[0],))
    off_custom = pd.read_csv(drPath + 'offset_custom.txt', sep=' ', header=None).values
    off_custom = np.reshape(off_custom, (off_custom.shape[0],))

    # initialize lock for avoiding race conditions in threads
    lock = Lock()

    # global variable accessed by main and mediapipe threads that contains the current vector of body landmarks
    global body
    body = np.zeros((num_joints,))  # initialize global variable

    # start thread for OpenCV. current frame will be appended in a queue in a separate thread
    q_frame = queue.Queue()
    cal = 0
    opencv_thread = Thread(target=get_data_from_camera, args=(cap, q_frame, r, cal))
    opencv_thread.start()
    print("openCV thread started in practice.")

    # initialize thread for mediapipe operations
    mediapipe_thread = Thread(target=mediapipe_forwardpass,
                              args=(holistic, mp_holistic, lock, q_frame, r, num_joints, joints))
    mediapipe_thread.start()
    print("mediapipe thread started in practice.")

    # initialize thread for writing reaching log file
    wfile_thread = Thread(target=write_practice_files, args=(r, timer_practice))
    timer_practice.start()  # start the timer for PracticeLog
    wfile_thread.start()
    print("writing reaching log file thread started in practice.")

    print("cursor control thread is about to start...")

    # -------- Main Program Loop -----------
    while not r.is_terminated:
        # --- Main event loop
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                r.is_terminated = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                    r.is_terminated = True
                if event.key == pygame.K_p:  # Pressing the p Key will pause/resume the game
                    reaching_functions.pause_acquisition(r, timer_practice)
                if event.key == pygame.K_SPACE:  # Pressing the space Key will click the mouse
                    pyautogui.click(r.crs_x, r.crs_y)

        if not r.is_paused:
            # Copy old cursor position
            r.old_crs_x = r.crs_x
            r.old_crs_y = r.crs_y

            # get current value of body
            r.body = np.copy(body)

            # apply BoMI forward map to body vector to obtain cursor position.
            r.crs_x, r.crs_y,r.online_crs_radius = reaching_functions.update_3D_cursor_position \
                (r.body, map, rot_dr, scale_dr, off_dr, rot_custom, scale_custom, off_custom)

            # Check if the crs is bouncing against any of the 4 walls:
            if r.crs_x >= r.width:
                r.crs_x = r.width
            if r.crs_x <= 0:
                r.crs_x = 0
            if r.crs_y >= r.height:
                r.crs_y = 0
            if r.crs_y <= 0:
                r.crs_y = r.height
            
            #check if the radius is acceptable ( )
            if r.online_crs_radius < 1:
                r.online_crs_radius = 1
            if r.online_crs_radius > r.crs_range:
                r.online_crs_radius = r.crs_range

            # Filter the cursor
            r.crs_x, r.crs_y = reaching_functions.filter_cursor(r, filter_curs)

            # if mouse checkbox was enabled do not draw the reaching GUI,
            # only change coordinates of the computer cursor !!!!!!!!!!!!!!!!!!!!!
            # [ADD CODE HERE] !!!!!!!!!!!!!!!!!!!!!


            # else: do the reaching

            # Set target position to update the GUI
            reaching_functions.set_target_reaching(r)
            # First, clear the screen to black. In between screen.fill and pygame.display.flip() all the draw
            screen.fill(BLACK)
            # Do not show the cursor in the blind trials when the cursor is outside the home target
            if not r.is_blind:
                #if crs radius < 20 --> GREEN 
                #if crs radius > 20 --> RED 
                # draw cursor
                if r.online_crs_radius <= 20:
                    pygame.draw.circle(screen, GREEN, (int(r.crs_x), int(r.crs_y)), r.online_crs_radius)
                elif r.online_crs_radius > 20:
                    pygame.draw.circle(screen, RED, (int(r.crs_x), int(r.crs_y)), r.online_crs_radius - 20)

            # draw target. green if blind, state 0 or 1. yellow if notBlind and state 2
            if r.state == 0:  # green
                pygame.draw.circle(screen, GREEN, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)
            elif r.state == 1:
                pygame.draw.circle(screen, GREEN, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)
            elif r.state == 2:  # yellow
                if r.is_blind:  # green again if blind trial
                    pygame.draw.circle(screen, GREEN, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)
                else:  # yellow if not blind
                    pygame.draw.circle(screen, YELLOW, (int(r.tgt_x), int(r.tgt_y)), r.tgt_radius, 2)

            # Display scores:
            font = pygame.font.Font(None, 80)
            text = font.render(str(r.score), True, RED)
            screen.blit(text, (1250, 10))

            # --- update the screen with what we've drawn.
            pygame.display.flip()

            # After showing the cursor, check whether cursor is in the target
            reaching_functions.check_target_reaching(r, timer_enter_tgt)
            # Then check if cursor stayed in the target for enough time
            reaching_functions.check_time_reaching(r, timer_enter_tgt, timer_start_trial, timer_practice)

            # update label with number of targets remaining
            tgt_remaining = 248 - r.trial + 1
            lbl_tgt.configure(text='Remaining targets: ' + str(tgt_remaining))
            lbl_tgt.update()

            # --- Limit to 50 frames per second
            clock.tick(50)

    # Once we have exited the main program loop, stop the game engine and release the capture
    pygame.quit()
    print("game engine object released in practice.")
    # pose.close()
    holistic.close()
    print("pose estimation object released in practice.")
    cap.release()
    cv2.destroyAllWindows()
    print("openCV object released in practice.")



def get_data_from_camera(cap, q_frame, r, cal):
    '''
    function that runs in the thread to capture current frame and put it into the queue
    :param cap: object of OpenCV class
    :param q_frame: queue to store current frame
    :param r: object of Reaching class
    :return:
    '''
    while not r.is_terminated:
        if not r.is_paused:
            ret, frame = cap.read()
            q_frame.put(frame)
            # if cal == 1:
            #    cv2.imshow('current frame', frame)
    print('OpenCV thread terminated.')

def save_video_calib(cap, q_frame, r, cal):
    '''
    function that runs in the thread to capture current frame and put it into the queue
    :param cap: object of OpenCV class
    :param q_frame: queue to store current frame
    :param r: object of Reaching class
    :return:
    '''
    #Define video_calib path
    video_calib_path = os.path.dirname(os.path.abspath(__file__)) + "/video_calib_rec/"

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_calib_path + 'calibration.avi', fourcc, 20.0, (640, 480))

    while not r.is_terminated:
        if not r.is_paused:
            ret, frame = cap.read()
            q_frame.put(frame)
            
            # output the frame
            out.write(frame) 
            
            # The original input frame is shown in the window 
            cv2.imshow('Original', frame)
        
            # if cal == 1:
            #    cv2.imshow('current frame', frame)
    print('OpenCV thread terminated.')


def mediapipe_forwardpass(holistic, mp_holistic, lock, q_frame, r, num_joints, joints):
    """
    function that runs in the thread for estimating pose online
    :param pose: object of Mediapipe class used to predict poses
    :param mp_pose: object of Mediapipe class for extracting body landmarks
    :param lock: lock for avoiding race condition on body vector
    :param q_frame: queue where to append current webcam frame
    :param r: object of Reaching class
    :return:
    """
    global body
    while not r.is_terminated:
        if not r.is_paused:
            # not sure if we want to put try/catch here, just in case "ask forgiveness, not permission"
            # try:
            # get current frame from thread
            curr_frame = q_frame.get()
            body_list = []

            # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(curr_frame, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to pass by reference.
            image.flags.writeable = False
            results = holistic.process(image)   

            if not results.pose_landmarks:
                continue
            if joints[0, 0] == 1:
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y)
            if joints[1, 0] == 1:
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EYE].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EYE].y)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].y)
            if joints[2, 0] == 1:
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER].y)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER].y)
            if joints[3, 0] == 1 or joints[4, 0] == 1:
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].y)
            if joints[4, 0] == 1:
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP].y)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP].y)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.RING_FINGER_TIP].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.RING_FINGER_TIP].y)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.PINKY_TIP].x)
                body_list.append(results.pose_landmarks.landmark[mp_holistic.HandLandmark.PINKY_TIP].y)

            body_mp = np.array(body_list)
            q_frame.queue.clear()
            with lock:
                body = np.copy(body_mp)
            # except:
            #     print('Expection in mediapipe_forwardpass. Closing thread')
            #     r.is_terminated = True
    print('Mediapipe_forwardpass thread terminated.')


def write_practice_files(r, timer_practice):
    """
    function that runs in the thread for writing reaching log in a file
    :param r: object of Reaching class
    :param timer_practice: stopwatch that keeps track of elapsed time during reaching
    :return:
    """
    while not r.is_terminated:
        if not r.is_paused:
            starttime = time.time()

            log = str(timer_practice.elapsed_time) + "\t" + '\t'.join(map(str, r.body)) + "\t" + str(r.crs_x) + "\t" + \
                  str(r.crs_y) + "\t" + str(r.block) + "\t" + \
                  str(r.repetition) + "\t" + str(r.target) + "\t" + str(r.trial) + "\t" + str(r.state) + "\t" + \
                  str(r.comeback) + "\t" + str(r.is_blind) + "\t" + str(r.at_home) + "\t" + str(r.count_mouse) + "\t" + \
                  str(r.score) + "\n"

            with open(r.path_log + "PracticeLog.txt", "a") as file_log:
                file_log.write(log)

            # write @ 50 Hz
            time.sleep(0.033 - ((time.time() - starttime) % 0.033))

    print('Writing reaching log file thread terminated.')



# CODE STARTS HERE
if __name__ == "__main__":
    # initialize mainApplication tkinter window
    win = tk.Tk()
    win.title("BoMI Settings")

    window_width = 1200
    window_height = 520

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))

    win.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

    MainApplication(win)

    # initiate Tkinter mainloop
    win.mainloop()
