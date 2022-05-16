import numpy as np
import pandas as pd
import math
from scipy import signal as sgn

import os


def write_header(r):
    # First check whether Practice folder exists. If not, create it
    if not os.path.exists(r.path_log):
        os.mkdir(r.path_log)

    header = "time\tnose_x\tnose_y\tr_shoulder_x\tr_shoulder_y\tl_shoulder_x\tl_shooulder_t\tcursor_x\tcursor_y\tblock\t"\
             "repetition\ttarget\ttrial\tstate\tcomeback\tis_blind\tat_home\tcount_mouse\tscore\n"
    with open(r.path_log + "PracticeLog.txt", "w+") as file_log:
        file_log.write(header)


def initialize_targets(r):
    """
    function that initializes list for target positions (x and y)
    :param r: object of the class Reaching. Use the class to change parameters of the reaching task
    :return:
    """
    r.empty_tgt_x_list()
    r.empty_tgt_y_list()
    for i in range(r.tot_targets[r.block - 1]):
        r.tgt_x_list.append(
            (r.width / 2) + r.tgt_dist * np.cos(
                (2 * i * np.pi / r.tot_targets[r.block - 1]) + np.pi / r.tot_targets[r.block - 1]))
        r.tgt_y_list.append(
            (r.height / 2) + r.tgt_dist * np.sin(
                (2 * i * np.pi / r.tot_targets[r.block - 1]) + np.pi / r.tot_targets[r.block - 1]))


def set_target_reaching_customization(r):
    """
    set position of current targ
    :return:
    """
    if r.comeback == 0:
        r.tgt_x = r.tgt_x_list[r.list_tgt[r.trial - 1]]
        r.tgt_y = r.tgt_y_list[r.list_tgt[r.trial - 1]]
    else:
        # When returning to home target visual feedback is restored
        r.is_blind = 0
        r.tgt_x = r.width / 2
        r.tgt_y = r.height / 2  # Center of the screen

    

def set_target_reaching(r):
    """
    set position of current targ
    :return:
    """
    if r.comeback == 0:
        r.tgt_x = r.tgt_x_list[r.list_tgt[r.trial - 1]]
        r.tgt_y = r.tgt_y_list[r.list_tgt[r.trial - 1]]
    else:
        # When returning to home target visual feedback is restored
        r.is_blind = 0
        r.tgt_x = r.width / 2
        r.tgt_y = r.height / 2  # Center of the screen


def filter_cursor(r, filter_curs):

    filter_curs.update_cursor(r.crs_x, 0)
    filter_curs.update_cursor(r.crs_y, 1)

    return filter_curs.filtered_value[0], filter_curs.filtered_value[1]


def update_cursor_position_custom(body, map, rot, scale, off):

    if type(map) != tuple:
        cu = np.dot(body, map)
    else:
        h = np.tanh(np.dot(body, map[0][0]) + map[1][0])
        h = np.tanh(np.dot(h, map[0][1]) + map[1][1])
        cu = np.dot(h, map[0][2]) + map[1][2]

    # Applying rotation
    cu[0] = cu[0] * np.cos(np.pi / 180 * rot) - cu[1] * np.sin(np.pi / 180 * rot)
    cu[1] = cu[0] * np.sin(np.pi / 180 * rot) + cu[1] * np.cos(np.pi / 180 * rot)

    # Applying scale
    cu = cu * scale

    # Applying offset
    cu = cu + off

    return cu[0], cu[1]


def update_cursor_position(body, map, rot_ae, scale_ae, off_ae, rot_custom, scale_custom, off_custom):

    if type(map) != tuple:
        cu = np.dot(body, map)
    else:
        h = np.tanh(np.dot(body, map[0][0]) + map[1][0])
        h = np.tanh(np.dot(h, map[0][1]) + map[1][1])
        cu = np.dot(h, map[0][2]) + map[1][2]

    # Applying rotation, scale and offset computed after AE training
    cu[0] = cu[0] * np.cos(np.pi / 180 * rot_ae) - cu[1] * np.sin(np.pi / 180 * rot_ae)
    cu[1] = cu[0] * np.sin(np.pi / 180 * rot_ae) + cu[1] * np.cos(np.pi / 180 * rot_ae)
    cu = cu * scale_ae
    cu = cu + off_ae

    # Applying rotation, scale and offset computed after customization
    cu[0] = cu[0] * np.cos(np.pi / 180 * rot_custom) - cu[1] * np.sin(np.pi / 180 * rot_custom)
    cu[1] = cu[0] * np.sin(np.pi / 180 * rot_custom) + cu[1] * np.cos(np.pi / 180 * rot_custom)
    cu = cu * scale_custom
    cu = cu + off_custom

    return cu[0], cu[1]


def write_practice_files(r, body, timer_practice):

    log = str(timer_practice.elapsed_time) + "\t" + '\t'.join(map(str, body)) + "\t" + str(r.crs_x) + "\t" + str(r.crs_y) + "\t" + str(r.block) + "\t" + \
          str(r.repetition) + "\t" + str(r.target) + "\t" + str(r.trial) + "\t" + str(r.state) + "\t" + \
          str(r.comeback) + "\t" + str(r.is_blind) + "\t" + str(r.at_home) + "\t" + str(r.count_mouse) + "\t" + \
          str(r.score) + "\n"

    with open(r.path_log + "PracticeLog.txt", "a") as file_log:
        file_log.write(log)


def check_target_reaching(r, timer_enter_tgt):
    """
    Check if cursor is inside the target
    """
    dist = np.sqrt((r.crs_x - r.tgt_x) ** 2 + (r.crs_y - r.tgt_y) ** 2)
    # If you are not in a blind trial
    if r.is_blind == 0:
        if dist < r.tgt_radius:
            # if cursor is inside the target: start the timer that will count for how long the cursor will stay in the
            # target, then change status (INSIDE target)
            if r.state == 0 or r.state == 1:
                timer_enter_tgt.start()
            r.state = 2
        # if cursor is inside the target (or if it used to be but currently is not) then go back at state 0
        # (OUT OF target, IN TIME) and reset timer
        else:
            r.state = 0
            # timer_enter_tgt.reset()  # Stops time interval measurement and resets the elapsed time to zero.
            timer_enter_tgt.start()

    # If blind trial -> stopping criterion is different
    # (cursor has to remain in a specific region for 2000 ms (50 Hz -> count_mouse == 100)
    else:
        if (r.old_crs_x + 10 > r.crs_x > r.old_crs_x - 10 and
                r.old_crs_y + 10 > r.crs_y > r.old_crs_y - 10 and r.at_home == 0):
            r.count_mouse += 1
        else:
            r.count_mouse = 0

    # Check here if the cursor is in the home target. In this case modify at_home to turn on/off the visual feedback
    # if the corresponding checkbox is selected
    if (r.repetition > 5 and
            (r.block == 2 or r.block == 3 or r.block == 4 or r.block == 5 or
             r.block == 7 or r.block == 8 or r.block == 9 or r.block == 10)):
        if (r.tgt_x_list[r.list_tgt[r.trial - 2]] - r.tgt_radius < r.crs_x < r.tgt_x_list[
            r.list_tgt[r.trial - 2]] + r.tgt_radius and
                r.tgt_y_list[r.list_tgt[r.trial - 2]] - r.tgt_radius < r.crs_y < r.tgt_y_list[
                    r.list_tgt[r.trial - 2]] + r.tgt_radius):
            r.at_home = 1
        else:
            r.at_home = 0

def check_region_cursor(r,timer_enter_region):
    """
    Check in what region the cursor is
    """
    #Check if the cursor is in the left side of the screen ( RES = 1800x900)
    if (r.crs_x > 0 and r.crs_x < 597):

        if (r.crs_y >= 0 and r.crs_y <= 297):
            if r.region != 1:
                timer_enter_region.start()
            r.region = 1

        elif (r.crs_y >= 303 and r.crs_y <= 597):
            if r.region != 4:
                timer_enter_region.start()
            r.region = 4

        elif (r.crs_y >= 603 and r.crs_y <= 897):
            if r.region != 7:
                timer_enter_region.start()
            r.region = 7

    elif (r.crs_x >= 603 and r.crs_x <= 1197):

        if (r.crs_y >= 0 and r.crs_y <= 297):
            if r.region != 2:
                timer_enter_region.start()
            r.region = 2

        elif (r.crs_y >= 303 and r.crs_y <= 597):
            if r.region != 5:
                timer_enter_region.start()
            r.region = 5

        elif (r.crs_y >= 603 and r.crs_y <= 897):
            if r.region != 8:
                timer_enter_region.start()
            r.region = 8

    elif (r.crs_x >= 1203 and r.crs_x <= 1797):

        if (r.crs_y >= 0 and r.crs_y <= 297):
            if r.region != 3:
                timer_enter_region.start()
            r.region = 3

        elif (r.crs_y >= 303 and r.crs_y <= 597):
            if r.region != 6:
                timer_enter_region.start()
            r.region = 6

        elif (r.crs_y >= 603 and r.crs_y <= 897):
            if r.region != 9:
                timer_enter_region.start()
            r.region = 9
        #///////////////////////////////////////////////////#

def check_time_region(r,timer_enter_region):
    """
    Assume to stay into a region for 250 ms
    Check if the time needed is elapsed.
    If yes set the corresponding lin and ang vel
    If no set to default 0
    """
    if timer_enter_region.elapsed_time > 250:
        compute_vel(r)
    else:
        r.lin_vel = 0.0
        r.ang_vel = 0.0
        
        
def compute_vel(r):
    """
    Given the region compute the velocities
    """
    if r.region == 1:
        r.lin_vel = 1.0
        r.ang_vel = 0.5
    elif r.region == 2:
        r.lin_vel = 1.0
        r.ang_vel = 0.0
    elif r.region == 3:
        r.lin_vel = 1.0
        r.ang_vel = -0.5
    elif r.region == 4:
        r.lin_vel = 0.0
        r.ang_vel = 0.5
    elif r.region == 5:
        r.lin_vel = 0.0
        r.ang_vel = 0.0
    elif r.region == 6:
        r.lin_vel = 0.0
        r.ang_vel = -0.5
    elif r.region == 7:
        r.lin_vel = -1.0
        r.ang_vel = 0.5
    elif r.region == 8:
        r.lin_vel = -1.0
        r.ang_vel = 0.0
    elif r.region == 9:
        r.lin_vel = -1.0
        r.ang_vel = -0.5
        

def check_joint_button(r,timer_enter_button,timer_enter_arrow):
    """
    Function that check what button is selected given crs_x crs_y,
    the center of the button and its weight (250 pixel) and hight (70 pixel)
    Once the button is selected timer_enter_button starts
    """
    #Check joint button 1
    if ((r.crs_x >= 225 - 125 and r.crs_x <= 225 + 125) and (r.crs_y >= 100 - 35 and r.crs_y <= 100 + 35)):
        if r.joint_button != 1:
            timer_enter_button.start()
        r.joint_button = 1
    
    #check joint button 2
    elif ((r.crs_x >= 675 - 125 and r.crs_x <= 675 + 125) and (r.crs_y >= 100 - 35 and r.crs_y <= 100 + 35)):
        if r.joint_button != 2:
            timer_enter_button.start()
        r.joint_button = 2
   
    #check button 3
    elif ((r.crs_x >= 1125 - 125 and r.crs_x <= 1125 + 125) and (r.crs_y >= 100 - 35 and r.crs_y <= 100 + 35)):
        if r.joint_button != 3:
            timer_enter_button.start()
        r.joint_button = 3
    
    #check button 4
    elif ((r.crs_x >= 1575 - 125 and r.crs_x <= 1575 + 125) and (r.crs_y >= 100 - 35 and r.crs_y <= 100 + 35)):
        if r.joint_button != 4:
            timer_enter_button.start()
        r.joint_button = 4
    
    #check button 5
    elif ((r.crs_x >= 450 - 125 and r.crs_x <= 450 + 125) and (r.crs_y >= 250 - 35 and r.crs_y <= 250 + 35)):
        if r.joint_button != 5:
            timer_enter_button.start()
        r.joint_button = 5
    
    #check button 6
    elif ((r.crs_x >= 900 - 125 and r.crs_x <= 900 + 125) and (r.crs_y >= 250 - 35 and r.crs_y <= 250 + 35)):
        if r.joint_button != 6:
            timer_enter_button.start()
        r.joint_button = 6
    
    #check button 7
    elif ((r.crs_x >= 1350 - 125 and r.crs_x <= 1350 + 125) and (r.crs_y >= 250 - 35 and r.crs_y <= 250 + 35)):
        if r.joint_button != 7:
            timer_enter_button.start()
        r.joint_button = 7

    #check button 8
    elif ((r.crs_x >= 900 - 125 and r.crs_x <= 900 + 125) and (r.crs_y >= 400 - 35 and r.crs_y <= 400 + 35)):
        if r.joint_button != 8:
            timer_enter_button.start()
        r.joint_button = 8

    #check up arrow box
    elif ((r.crs_x >= 300 and r.crs_x <= 600) and (r.crs_y >= 550 and r.crs_y <= 850)):
        if r.up_arrow == False:
            timer_enter_arrow.start()
        r.up_arrow = True


    #check down arrow box
    elif ((r.crs_x >= 1200 and r.crs_x <= 1500) and (r.crs_y >= 550 and r.crs_y <= 850)):
        if r.down_arrow == False:
            timer_enter_arrow.start()
        r.down_arrow = True

    #if is not in any button restart timers
    #cursor is not in the arrows
    #set button to zero
    else:
        timer_enter_button.start()
        timer_enter_arrow.start()
        r.joint_button = 0
        r.up_arrow = False
        r.down_arrow = False

def check_sel_button(r,timer_enter_button,timer_enter_arrow):
    """
    This function is used to select one button
    The button is selected only if the cursor
    remains into the button for more than 250ms
    """
    if (timer_enter_button.elapsed_time > 250) and (r.joint_button != 0):
        r.sel_button = r.joint_button
    elif (timer_enter_arrow.elapsed_time > 250) and (r.up_arrow == True):
        #increment the selected joint
        #restart timer
        increment_joint(r)
        timer_enter_arrow.start()
    elif (timer_enter_arrow.elapsed_time > 250) and (r.down_arrow == True):
        #decrement the selected joint
        #restart timer
        decrement_joint(r)
        timer_enter_arrow.start()

def increment_joint(r):
    """
    Function that increments the selected joint
    it also limits the value
    """
    r.joint_state[r.sel_button - 1] = r.joint_state[r.sel_button - 1] + 0.1
    if r.joint_state[r.sel_button - 1] <= 0:
        r.joint_state[r.sel_button - 1] = 0
    elif r.joint_state[r.sel_button - 1] >= math.pi:
        r.joint_state[r.sel_button - 1] = math.pi


def decrement_joint(r):
    """
    Function that decrements the selected joint
    it also limits the value
    """
    r.joint_state[r.sel_button - 1] = r.joint_state[r.sel_button - 1] - 0.1
    if r.joint_state[r.sel_button - 1] <= 0:
        r.joint_state[r.sel_button - 1] = 0
    elif r.joint_state[r.sel_button - 1] >= math.pi:
        r.joint_state[r.sel_button - 1] = math.pi



def check_time_reaching(r, timer_enter_tgt, timer_start_trial, timer_practice):
    if r.state == 0:  # OUT OF target, IN TIME
        # if more than 1s is elapsed from beginning of the reaching:
        # change status(OUT OF target, OUT OF TIME) -> cursor red
        if timer_start_trial.elapsed_time > 1000:
            r.state = 1
    # BLIND TRIAL: cursor must stay in a specific region(+-50 pxl) for 100 ticks(100 * 20ms = 2000ms)
    if r.is_blind == 1 and r.count_mouse == 100:
        r.is_blind = 0

    # VISUAL FEEDBACK ON: cursor must stay inside the target for 250 ms.
    if r.is_blind == 0 and r.state == 2 and timer_enter_tgt.elapsed_time > 250:
        # timer_enter_tgt.reset()  # Stops time interval measurement and resets the elapsed time to zero.
        timer_enter_tgt.start()
        r.count_mouse = 0
        r.state = 0  # a new reaching will begin.state back to 0 (OUT OF target, IN TIME) -> cursor green

        if timer_start_trial.elapsed_time < 2000:
            r.score += 4
        elif timer_start_trial.elapsed_time < 3000:
            r.score += 3
        elif timer_start_trial.elapsed_time < 4000:
            r.score += 2
        else:
            r.score += 1

        # Random Walk
        if r.block == 2 or r.block == 3 or r.block == 4 or r.block == 5 or r.block == 7 or r.block == 8 or r.block == 9 or r.block == 10:
            if r.comeback == 0:  # going towards peripheral targets
                # Never comeback home
                # if you finished a repetition
                if r.target == r.tot_targets[r.block - 1] - 1:
                    r.target = 0
                    r.repetition += 1
                else:
                    r.target += 1

                # if you're entering the last repetition -> is_blind = true
                if r.repetition == r.tot_repetitions[r.block - 1]:
                    r.is_blind = 1
                r.trial += 1

            else:  # going towards home target (used just at the beginning of the experiment)
                r.comeback = 0

        # Center-Out
        else:
            if r.comeback == 0:  # going towards peripheral targets
                # next go to home tgt
                r.comeback = 1
                r.target += 1

                # if you finished a repetition
                # (last tgt don't come back home, just update trial and repetition and reset target)
                if r.target == r.tot_targets[r.block - 1]:
                    r.target = 0
                    r.repetition += 1
                    r.trial += 1
                    r.comeback = 1
            else:  # going towards home target (used just at the beginning of the experiment)
                # next go to peripheral tgt
                r.comeback = 0
                if r.target != 0:
                    r.trial += 1

        # pause acquisition if you have finished all repetitions.
        if r.repetition > r.tot_repetitions[r.block - 1]:
            pause_acquisition(r, timer_practice)

            r.score = 0
            r.is_blind = 1
            r.target = 0
            r.comeback = 1
            r.repetition = 1

            # stop if you finished all the blocks
            if r.block == r.tot_blocks:
                stop_thread(r)
                print("Practice is finished!")

            else:
                r.block += 1
                initialize_targets(r)

        # timer_start_trial.restart()  # restart is a reset + start
        timer_start_trial.start()  # Restart timer that keeps track of time elapsed since the beginning of the reach


def pause_acquisition(r, timer_practice):
    # If you are doing the reaching, stop the acquisition timer and sensors thread
    if not r.is_paused:
        timer_practice.pause()
        r.is_paused = True
        print("Pausing reaching...")

    # Resume reaching
    else:
        r.is_paused = False
        timer_practice.restart()
        print("Resuming reaching...")


def stop_thread(r):
    r.is_terminated = True
    print("main thread: Worker thread has terminated.")


def filt(N, fc, fs, btype, signal):
    """
        Function that filters an input signal (with Butterworth IIR)
        :param N: order of the filter
        :param fc: cutoff frequency
        :param fs: sampling frequency of input signal
        :param btype: type of filter {‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’}
        :param signal: input signal to be filtered
        :return: filtered signal
    """
    Wn = fc / (fs / 2)
    b, a = sgn.butter(N, Wn, btype)

    return pd.Series(sgn.lfilter(b, a, signal))











