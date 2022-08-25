#!/bin/bash

source ~/tiago_public_ws/devel/setup.bash

#Semplice spawn tiago in gazebo senza moduli per testare nine region gui
#gnome-terminal --tab --title="small_office_navigation" -- bash -c "roslaunch tiago_gazebo tiago_gazebo.launch public_sim:=true robot:=titanium world:=simple_office_with_people"

#Spawn Gazebo + Rviz + navigation pkg + AMCL + move base + mapping
gnome-terminal --tab --title="small_office_navigation" -- bash -c "roslaunch tiago_2dnav_gazebo tiago_navigation.launch public_sim:=true world:=simple_office_with_people "


source ~/my_ros_ws/devel/setup.bash
gnome-terminal --tab --title="cmd_vel_pub" -- bash -c "sleep 10; rosrun my_tiago cmd_vel_publisher.py"
# Da aggiungere nascondi terminale
#xdotool windowminimize $(xdotool getactivewindow)


