#!/usr/bin/env python

# -- Import ROS libraries -- #
from cmath import sin

from numpy import tri
import rospy
from std_msgs.msg import *
import tf
from tf.transformations import quaternion_from_euler
from geometry_msgs.msg import PoseStamped
import moveit_commander
import moveit_msgs.msg
import math

class TeleoperationArm:
    def __init__(self):

        # -- ROS Subcriber -- #
        self.tf_listener = None
        self.amplitude_sub = None
        self.angle_sub = None
        self.arm_state_sub = None
        self.map_name_sub = None

        # -- Variables -- #
        self.vector_amplitude = None
        self.vector_angle = None
        self.received_angle = False
        self.received_amplitude = False
        self.tf_translation = None
        self.arm_state = 1.0

        # -- TIAGo arm valid space (for TIAGo one arm) -- #
        # -- Translation of the arm_tool_link with respect to base_footprint -- #
        self.min_x = 0.35 #minimum extension
        self.max_x = 0.6  #maximum extension
        self.min_y = -0.5 #maximum right
        self.max_y = 0.5  #maximum left
        self.min_z = 0.45 #minimum altitude
        self.max_z = 1.3  #maximum altitude
        self.z_range = 1.3 - 0.45
        
        # -- 1D vector amplitude range -- #
        self.max_1D_amplitude = 450
        self.min_1D_amplitude = 0

        # -- To receive the map -- #
        self.map_name = None

        # -- Assumption: Gripper Parallel to the ground --#
        self.parallel_gripper = quaternion_from_euler(math.pi/2,0,0)

        # -- Predefined Configuration TIAGo one Arm -- #
        # -- Format (x,y,z,rx,ry,rz)
        self.predefined_pose = [0.6,0,0.6,self.parallel_gripper[0],self.parallel_gripper[1],self.parallel_gripper[2],self.parallel_gripper[3]]
        self.first_plan = False

teleoperate_arm = TeleoperationArm()

def amplitude_clbk(msg):
    """"
    This simple funciton corresponds to the vector amplitude callback function
    It simply updates the value of the vector amplitude inside the global object teleoperate_arm
    """ 
    global teleoperate_arm
    print("Vector Amplitude corretly updated")
    teleoperate_arm.vector_amplitude = msg.data
    teleoperate_arm.received_amplitude = True

def angle_clbk(msg):
    """"
    This simple funciton corresponds to the vector angle callback function
    It simply updates the value of the vector angle inside the global object teleoperate_arm
    """
    global teleoperate_arm
    print("Vector Angle corretly updated")
    teleoperate_arm.vector_angle = msg.data
    teleoperate_arm.received_angle = True

def arm_state_clbk(msg):
    """
    This function simply updates the arm teleoperation state
    In particular:
        - If the value is equal to 0.0 --> 1D vector
        - If the value is equal to 1.0 --> 2D vector
    """
    global teleoperate_arm
    teleoperate_arm.arm_state = msg.data
    print("Arm State correctly updated")

def map_name_clbk(msg):
    """
    This function simply updates the map of the simulation
    """
    global teleoperate_arm
    if msg.data == 1.0:
        teleoperate_arm.map_name = "simple_office"
    elif msg.data == 2.0:
        teleoperate_arm.map_name = "simple_office_with_people"
    elif msg.data == 3.0:
        teleoperate_arm.map_name = "real_tiago"
    

def compute_1D_motion(translation):
    """
    This function, starting from the actual position of the arm_tool_link with respect to base_footprint
    and knowing the amplitude and the angle of the vector, computes the new position of the arm_tool_link frame
    Assumption: the orientation of the frame is constant and equal to [pi/2 , 0 , 0] (gripper parallel to the ground)
    In particular this function is used for the "1D vector" arm state, where our purpose is to control the z component
    Parameter:
        -translation: is a triple (x,y,z) that indicates the actual position of the arm_tool_link with respect to base_footprint
    Return:
        -translation: [x,y,z] with the z value modified
    """
    global teleoperate_arm
    angle = teleoperate_arm.vector_angle
    amplitude = teleoperate_arm.vector_amplitude

    # -- y = 0.00188889x represent the linear transformation that map 
    # -- 0 - 450 --> 0 - 0.85
    transform = 0.00188889

    # -- Only two measures of angle are valid --# 
    if angle == 90:
        # -- The goal is to augment the z coordinate -- #
        translation[2] = translation[2] + amplitude * transform

    elif angle == 270:
        # -- The goal is to decrease the z coordinate -- #
        translation[2] = translation[2] - amplitude * transform
    else:
        print("1D vector angle not valid!")

    # -- Limit the z component -- #
    if translation[2] > teleoperate_arm.max_z:
        translation[2] = teleoperate_arm.max_z
    elif translation[2] < teleoperate_arm.min_z:
        translation[2] = teleoperate_arm.min_z

    return translation


def compute_2D_motion(translation):
    """
    This function, starting from the actual position of the arm_tool_link with respect to base_footprint
    and knowing the amplitude and the angle of the vector, computes the new position of the arm_tool_link frame
    Assumption: the orientation of the frame is constant and equal to [pi/2 , 0 , 0] (gripper parallel to the ground)
    In particular this function is used for the "2D vector" arm state, where our purpose is to control the x and y components
    The angle indicates how to change the components
    Explaination:
        If the angle is 90/270 degree, it simply means that the only component that will be affected is the x component
        If the angle is 0/180 the only component that will be affected is the y component
        All the angles between have to be mapped in order to modify both x and y components
    Parameter:
        -translation: is a triple (x,y,z) that indicates the actual position of the arm_tool_link with respect to base_footprint
    Return:
        -translation: [x,y,z] with the z value modified
    """  
    global teleoperate_arm

    print("Entered in the function the translation is: " + str(list(translation)))
    
    # -- Store locally angle (in degree) and amplitude of the vector -- #
    angle = teleoperate_arm.vector_angle
    angle_radians = math.radians(angle)
    amplitude = teleoperate_arm.vector_amplitude    

    # -- Amplitude range for 2D vector is [0 - 1006] --#
    # -- Transform is a factor that map linearly: 
    # -- [0-450] --> [0 - 0.25] for x component 
    # -- [0-900] --> [0 - 1] for y component -- #

    transform_x = 0.000555556 #(0.25 / 450)
    transform_y = 0.001111111 #(1/900)
 
    print("Amplitude: " + str(amplitude) + " Angle: " + str(angle))

    # -- Four cases depending on the angle 's value -- #
    # -- Angle it is important to understand how components change -- # 
    # -- scaling_factor belongs to [0,1] -- #

    # -- x increase y decrease -- #
    if angle <= 90 and angle >= 0:
        print("Case 1")

        # --Decompose Amplitude along x and y component -- #
        x_amplitude = amplitude * math.sin(angle_radians)
        print("Sin Result: " + str(math.sin(angle_radians)))
        y_amplitude = amplitude  * math.cos(angle_radians)
        print("Cos Result: " + str(math.cos(angle_radians)))
        print("X amp: " + str(x_amplitude) + " Y amp: " + str(y_amplitude))
        
        # -- Found the scaling factor for the components -- #
        scaling_factor_x = angle / 90
        scaling_factor_y = 1 - (angle / 90)
        translation[0] = translation[0] - (transform_x * x_amplitude)
        translation[1] = translation[1] - (transform_y * y_amplitude)
        print("Product for x component : " + str(transform_x * x_amplitude))
        print("Product for y component " + str(transform_y * y_amplitude))

    # -- x increase y increase -- #
    elif angle <= 180 and angle > 90:
        print("Case 2")
        
        # --Decompose Amplitude along x and y component -- #
        triangle_angle = 180 - angle
        triangle_angle_radians = math.radians(triangle_angle)
        x_amplitude = amplitude * math.sin(triangle_angle_radians)
        print("Sin Result:   " + str(math.sin(triangle_angle_radians)))
        print("Cos Result: " + str(math.cos(triangle_angle_radians)))
        y_amplitude = amplitude  * math.cos(triangle_angle_radians)
        print("X amp: " + str(x_amplitude) + " Y amp: " + str(y_amplitude))

        # -- Found the scaling factor for the components -- #
        scaling_factor_x = 2 - (angle / 90)
        scaling_factor_y = (angle / 90) - 1
        translation[0] = translation[0] - (transform_x * x_amplitude)
        translation[1] = translation[1] - (transform_y * y_amplitude)
        print("Product for x component : " + str(transform_x * x_amplitude))
        print("Product for y component " + str(transform_y * y_amplitude))
         
    # -- x decrease y increase -- #
    elif angle > 180 and angle <= 270:
        print("Case 3")
        
        # --Decompose Amplitude along x and y component -- #
        triangle_angle = angle - 180
        triangle_angle_radians = math.radians(triangle_angle)
        x_amplitude = amplitude * math.sin(triangle_angle_radians)
        y_amplitude = amplitude  * math.cos(triangle_angle_radians)
        print("Sin Result: " + str(math.sin(triangle_angle_radians)))
        print("Cos Result: " + str(math.cos(triangle_angle_radians)))
        print("X amp: " + str(x_amplitude) + " Y amp: " + str(y_amplitude))

        # -- Found the scaling factor for the components -- #
        scaling_factor_x = (angle / 90) - 2
        scaling_factor_y = 3 - (angle / 90)
        translation[0] = translation[0] - (transform_x * x_amplitude)
        translation[1] = translation[1] + (transform_y * y_amplitude)
        print("Product for x component : " + str(transform_x * x_amplitude))
        print("Product for y component " + str(transform_y * y_amplitude))

    # -- x decrease y decrease -- #
    elif angle > 270 and angle <= 360:
        print("Case 4")

        # --Decompose Amplitude along x and y component -- #
        triangle_angle = 360 - angle
        triangle_angle_radians = math.radians(triangle_angle)
        x_amplitude = amplitude * math.sin(triangle_angle_radians)
        y_amplitude = amplitude  * math.cos(triangle_angle_radians)
        print("Sin Result: " + str(math.sin(triangle_angle_radians)))
        print("Cos Result: " + str(math.cos(triangle_angle_radians)))
        print("X amp: " + str(x_amplitude) + " Y amp: " + str(y_amplitude))

        # -- Found the scaling factor for the components -- #
        scaling_factor_x = 4 - (angle / 90)
        scaling_factor_y = (angle / 90) - 3
        # translation[0] = translation[0] - (scaling_factor_x * transform_x * x_amplitude) 
        # translation[1] = translation[1] - (scaling_factor_y * transform_y * y_amplitude)
        translation[0] = translation[0] - (transform_x * x_amplitude)
        translation[1] = translation[1] - (transform_y * y_amplitude)
        print("Product for x component : " + str(transform_x * x_amplitude))
        print("Product for y component " + str(transform_y * y_amplitude))

    # -- Limit the components to max or min -- #

    # -- Limit the x component --#
    if translation[0] > teleoperate_arm.max_x:
        translation[0] = teleoperate_arm.max_x
    
    elif translation[0] < teleoperate_arm.min_x:
        translation[0] = teleoperate_arm.min_x

    # -- Limit the y component -- #
    if translation[1] > teleoperate_arm.max_y:
        translation[1] = teleoperate_arm.max_y

    elif translation[1] < teleoperate_arm.min_y:
        translation[1] = teleoperate_arm.min_y

    print("Before Exit Translation is " + str(list(translation)) )

    return translation

def teleoperate_tiago_arm():
    """
    This function is the main function of the script
    In particular it declare all publishers and subcriber needed to teleoperate TIAGo arm.
    The information needed are already published by server_socket (amplitude and angle of the vectors)
    """
    global teleoperate_arm

    # -- Initialize moveit commmander -- #
    moveit_commander.roscpp_initialize(sys.argv)

    # Starts a new node
    print("Teleoperate Arm  [STARTED]")
    rospy.init_node('teleoperate_arm', anonymous=True)

    # -- Declare tf listener -- #
    teleoperate_arm.tf_listener = tf.TransformListener()
    
    # -- Declare rate -- #
    rate = rospy.Rate(10) #10 Hz

    # -- Declare all subscribers --#
    teleoperate_arm.amplitude_sub = rospy.Subscriber("server_socket/vector_amplitude",Int32,amplitude_clbk)
    teleoperate_arm.angle_sub  = rospy.Subscriber("server_socket/vector_angle",Int32,angle_clbk)
    teleoperate_arm.arm_state_sub = rospy.Subscriber("server_socket/arm_state",Float32,arm_state_clbk)
    teleoperate_arm.map_name_sub = rospy.Subscriber("server_socket/map_name",Float32,map_name_clbk)

    # -- MoveIt declaration -- #
    #tiago_robot = moveit_commander.RobotCommander()
    #scene = moveit_commander.PlanningSceneInterface()
    group_name = "arm_torso"
    group = moveit_commander.MoveGroupCommander(group_name)
    group.set_goal_tolerance(0.01)
    group.set_planner_id("SBLKConfigDefault")
    group.set_pose_reference_frame("base_footprint")
    
    display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',moveit_msgs.msg.DisplayTrajectory,queue_size=20)
       

    # -- Main loop until ropsy not shutdown --#
    while not rospy.is_shutdown():

        # -- Move TIAGo arm to the predefined configuration -- #
        while(not teleoperate_arm.first_plan):
            print(teleoperate_arm.predefined_pose)
            group.set_pose_target(teleoperate_arm.predefined_pose)
            group.set_start_state_to_current_state()
            group.set_max_velocity_scaling_factor(1.0)
            teleoperate_arm.first_plan = group.go(wait=True)

            if teleoperate_arm.first_plan:
                    print("Execution first plan finished successfully")
                    print("You can now start to send goals!!!")
                
            else:
                print("The first plan did not go through!")

            # -- Stop the motion to ensure residual motion and clear the target -- #
            group.stop()
            group.clear_pose_targets()

            rospy.sleep(1)

        # -- if the information about the vector (angle and amplitude) have been received --#
        if teleoperate_arm.received_angle and teleoperate_arm.received_amplitude:

            # -- If 1D vector state --#
            if teleoperate_arm.arm_state == 0.0:

                # -- Try to extract tf information between /base_footprint' and '/arm_tool_link -- #
                try:
                    (trans,rot) = teleoperate_arm.tf_listener.lookupTransform('/base_footprint', '/arm_tool_link', rospy.Time(0))
                except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                    continue

                print("Translation is: " + str(list(trans)) + " Rotation is: " + str(list(rot)))
                teleoperate_arm.tf_translation = trans

                #print("Angle :" + str(teleoperate_arm.received_angle) + " Amplitude: " + str(teleoperate_arm.received_amplitude))

                # -- Apply the vector to the actual position of the arm_tool_link w.r base_footprint -- #
                translation = compute_1D_motion(teleoperate_arm.tf_translation)
                print("Extracter translation: " + str(list(translation)))
                
                # # -- MoveIt IK --#
                # goal_pose = PoseStamped()
                # goal_pose.header.frame_id = "base_footprint"
                # goal_pose.pose.position.x = translation[0]
                # goal_pose.pose.position.y = translation[1]
                # goal_pose.pose.position.z = translation[2]


                # -- Gripper parallel to the ground -- #
                # goal_pose.pose.orientation = quaternion_from_euler(math.pi / 2, 0 , 0 )

                #orientation = quaternion_from_euler(math.pi / 2, 0 , 0 )
                #goal = [translation[0],translation[1],translation[2],orientation[0],orientation[1],orientation[2],orientation[3]]
                #goal = [0.6,0,0.6,orientation[0],orientation[1],orientation[2],orientation[3]]
                goal = [translation[0],translation[1],translation[2],teleoperate_arm.parallel_gripper[0],teleoperate_arm.parallel_gripper[1],teleoperate_arm.parallel_gripper[2],teleoperate_arm.parallel_gripper[3]]


                #print("Quaternion extracted : " + str(list(goal_pose.pose.orientation)))
                print("MoveIt is trying to bring the frame to " + str(list(goal)))

                # -- Set the target and Move the arm -- #
                group.set_pose_target(goal)
                group.set_start_state_to_current_state()
                group.set_max_velocity_scaling_factor(1.0)
                plan = group.go(wait=True)

                if plan:
                    print("Execution finished successfully")
                    print("You can now send another goal!!!")
                
                else:
                    print("The plan did not go through!")
                    print("You can now send another goal!!!")

                # -- Stop the motion to ensure residual motion and clear the target -- #
                group.stop()
                group.clear_pose_targets()

                # -- Restore to False for the next turn --#
                teleoperate_arm.received_amplitude = False
                teleoperate_arm.received_angle = False
        
            # -- If 2D vector arm teleoperation mode -- #
            elif teleoperate_arm.arm_state == 1.0:

                # -- Try to extract tf information between /base_footprint' and '/arm_tool_link -- #
                try:
                    (trans,rot) = teleoperate_arm.tf_listener.lookupTransform('/base_footprint', '/arm_tool_link', rospy.Time(0))
                except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                    continue

                print("Translation is: " + str(list(trans)) + " Rotation is: " + str(list(rot)))
                teleoperate_arm.tf_translation = trans
                
                # -- Apply the vector to the actual position of the arm_tool_link w.r base_footprint -- #
                translation = compute_2D_motion(teleoperate_arm.tf_translation)
                print("Extracter translation: " + str(list(translation)))

                # -- Define the goal as [x,y,z,qx,qy,qz,qw]
                goal = [translation[0],translation[1],translation[2],teleoperate_arm.parallel_gripper[0],teleoperate_arm.parallel_gripper[1],teleoperate_arm.parallel_gripper[2],teleoperate_arm.parallel_gripper[3]]


                #print("Quaternion extracted : " + str(list(goal_pose.pose.orientation)))
                print("MoveIt is trying to bring the frame to " + str(list(goal)))

                # -- Set the target and Move the arm -- #
                group.set_pose_target(goal)
                group.set_start_state_to_current_state()
                group.set_max_velocity_scaling_factor(1.0)
                plan = group.go(wait=True)

                if plan:
                    print("Execution finished successfully")
                    print("You can now send another goal!!!")
                
                else:
                    print("The plan did not go through!")
                    print("You can now send another goal!!!")

                # -- Stop the motion to ensure residual motion and clear the target -- #
                group.stop()
                group.clear_pose_targets()

                # -- Restore to False for the next turn --#
                teleoperate_arm.received_amplitude = False
                teleoperate_arm.received_angle = False
        
        #rospy.spin()
        rate.sleep()

if __name__ == '__main__':
    """
    Entry point of the program
    It executes the function demanded to teleoperate TIAGo arm until an execption fires
    """
    try:
        teleoperate_tiago_arm()
    except rospy.ROSInterruptException: 
        pass





