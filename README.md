# TIAGo_Teleoperation_MarkerLessBoMI Master Thesis Project
## Dr. Ermanno Girardo, Robotics Engineer.
![LogoUnige](https://user-images.githubusercontent.com/48509825/194903696-dc4fe201-b1b8-422d-a52a-4e00d44f9c65.png)

## Introduction
This project has been developed on the basis of an existent project that you can find [Clicking Here!](https://github.com/MoroMatteo/markerlessBoMI_FaMa).
In particular this project is aimed to create an architecture, which allow a tetraplegic subjects to teleoperate an assistive robot throw BoMI (Body Machine Interface).
If you are not confident with BoMI or you need more information about this project you can read **TIAGo robot teleoperation via Body Machine Interface for cervical Spinal Cord Injured subject assistance** pdf file that describes the work done for the master thesis.
The general idea is to exploit BoMI's potential in order to teleoperate TIAGo robot throw body motion (shoulders, eyes and nose) in order to teleoperate TIAGo's mobile base and its 7 DoF arm solving a reaching task problem.
Take in mind that a cSCI subject has lost motor functionalities under the level of the lesion and for this reason, most of the time these subjects have lost hands and arms functionalities.
This notebook wants to be a guide to explain the architecture and code in order to install and run all the architecture.
**Note** that is **mandatory** the usage of two different machines to run the simulation or to directly teleoperate TIAGo real robot.
In order to be clear as possible, the two machines, call them for semplicity 'BoMI Main Program' the machine where the BoMI program will run and will send all data to the second machine, call it 'ROS side' which will host Ubuntu Operating System in order to teleoperate TIAGo robot or simply run the simulation environment.
The two machines are able to communicate thanks to a TCP/IP socket communication, for this reason the two machines have to be under the same network**.

## 'BoMI Main Program Installing Procedure'
In order to install BoMI main program (all you need is inside **MarkerLessBoMI** folder you can follow [THIS!](https://github.com/MoroMatteo/markerlessBoMI_FaMa) repositoy.
As you can see you can install BoMI main program both on Ubuntu or Windows.

## 'ROS Side Program Installing Procedure'
On a second machine it is mandatory the usage of **Ubuntu** since you have to install **ROS** (Robotic Operating System), in order to teleoperate TIAGo both in simulation environment both the real TIAGo robot.
Since you have to install ROS **melodic** I suggest to you to download Ubuntu version **18.04 LTS**.
Once you have Ubunut 18.04 ready to use, you can proceede to install ROS melodic on your OS.
In order to install ROS melodic and all the packages needed to interact with TIAGo robot you can [Click Here!](http://wiki.ros.org/Robots/TIAGo/Tutorials/Installation/InstallUbuntuAndROS) and follow the installing procedure.
All you need to exectute the simulation is inside **my_tiago** folder, then create a new ROS workspace and copy it into the workspace.
You should be ready to execute the architecture environment.

## How to run the overall architecture
In order to run the overall architecture please follow the next steps:

I. Check ip address of your Ubuntu machine

II. Modify the ip address inside  **socket_client.py** inside **MarkerLessBoMI/scripts**, in particular it is declared inside **client_connected** function

III. Execute **server_socket.py** inside **my_tiago/scripts**, in order to allow ROS side machine to receive data from BoMI Main Program

IV. Execute **main_reaching.py** inside **MarkerLessBoMI** folder,  after some seconds should be appear the interface of BoMI main program, in figure below


![Screenshot (13)](https://user-images.githubusercontent.com/48509825/194919142-7b5df788-e2a3-4275-bfbf-31c2b10b4e4e.png)

<p align="center"> Figure 1: BoMI Main Program GUI </p>

## BoMI Main Program Brief Explanation
As you can see in the figure above, the home page of the BoMI main program has different functionalities.
In particular:
* Select the wanted joints to teleoperate TIAGo Robot
* Once selected the joints, clicking on the button **Calibration** is possible to acquire and store body data through 1 minute of body dance
* Before starting the calibration, you can fix the webcam clicking on the button **Show Webcam** in order to see the area acquired by the webcam.
* Calculate BoMI Map choosing Dimensionality Reduction technique among **Principal Component Analysis** (PCA), **AutoEncoder** (AE) and **Variational AutoEncoder** (VAE), for other details about BoMI and dimensionality reduction see Chapter 2
* **Customization** allows to customize BoMI map depending on the calibration, this is not mandatory.
* The subject can also make practice with BoMI thanks to a dedicated mode, clicking on **Practice** button, this is not mandatory but suggested.
* Clicking on the button **Eye Calibration** the subject performs 10 seconds eyes calibration. Eyes Calibration is mandatory and will be used by **eye_blink_detector.py** as a source of information in order to detect eye closure.
  During this calibration the subject has to open and close the eyes without squint too much, you can see the clip above in order to understand how to do a good calibration.
  See chapter 4 section 7 for more details.
 

https://user-images.githubusercontent.com/48509825/194934596-c1eced3a-17e2-4014-bf48-06ad025df2c7.mp4
  
* Clicking on the button **Nose Calibration** the subject performs 10 seconds nose calibration. Nose Calibration is mandatory and will be used by **nose_detector.py** to compute nose position 
  The calibration has to start with the face towards the camera and then move the nose right to an accessible and convenient pose.
  You can see the clip above in order to understand how to do a good calibration.
  

https://user-images.githubusercontent.com/48509825/194934751-48a98fda-da62-4b1a-a04b-29c23c6a2aa1.mp4

* Clicking on the button **TIAGo Practice** a new window will be displayed like in figure 2. If all went well the connection between BoMI main program machine and ROS machine should be opened.

![Screenshot (17)](https://user-images.githubusercontent.com/48509825/194936639-a1c46dea-a0be-43a8-996f-a11aeb114e31.png)

<p align="center"> Figure 2: TIAGo Practice Window </p>

As you can see, bofore selecting the wanted mode, the user has the possibility to select between two different maps in figure below in order to teleoperate TIAGo in Gazebo simulation enviroment, or teleoperate the real TIAGo.
  **Note** that you can teleoperate also TIAGo ++ verison (with two arms).
  

The user can choose between three different modes:
* Base teleoperation, where only the teleoperation of the base is possible in order to make practice with base teleoperation.
* Arm teleoperation, where only the teleoperation of the arm is possible in order to make practice with arm teleoperation.
* Free Mode, where it is possible to teleoperate both the arm and both the base.

## BoMI Main Program Content Description
In addition to **main_reaching.py** script there are also others python scripts that allow main program to work:








![Screenshot (16)](https://user-images.githubusercontent.com/48509825/194938795-b6c35a6c-b492-4d66-bf27-3871eefcb6bf.png)
<p align="center"> Figure 3: Scripts Three MarkerLess BoMI </p>


* **compute_bomi_map.py** allows the computation of the BoMI map importing PCA, AE and VAE models and using the collected body data

* **display_webcam.py** allows to show the webcam when the button **Show Webcam** is pressed

* **eye_blinking_detector.py** contains functions to make eyes calibration and to detect eyes blinking or closure for 2 seconds, signals that will be used to switch teleoperation mode or to select coordinates.

* **filter_butter_online.py** contains a class to perform online filter of the cursor

* **nose_detector.py** contains a function to make nose calibration and the observer to detect when the nose right cross the threshold

* **odom_server_TCP.py** is a trial file used to understand TCP connection. This file is not used.

* **reaching.py** defines a class that contains all the parameters for handling the reaching task

* **reaching_functions.py** contains a set of functions used to perform the reaching task

* **server_socket.py** is a copy of the file that runs ROS side. It is essentially the server socket and plays also the role of a decoder to scomppose the information from the client server. Also publishers and subscribers have been implemented in order to share data via topics.

* **setup.py** is a file with all the packages needed to run BoMI MarkerLess program.

* **socket_client.py** is essentially the client of the TCP/IP communication. This file contains a function to establish the connection with the server and also functions to parse data to be sent to the server socket.

* **stopwatch.py** contains a class that define a stopwatch object.

* **utils.py** is a collection of utils functions used to draw on image window.


## ROS Side Content Description
In this section I want to describe briefly **my_tiago** pkg.

![Screenshot (19)](https://user-images.githubusercontent.com/48509825/195090816-866b1ff8-0f0c-4f18-9255-3a0d83bebdb8.png)
<p align="center"> Figure 4: Scripts Three ROS Side </p>

In figure above there are also some scripts that are not used for simulation purpose.
The scripts that you have to consider are:
* **cmd_vel_publisher.py** is the script demanded to teleoperate TIAGo mobile base. In particular it contains a class used to share variables, methods, publishers and subscribers in order to receive data from **server_socket.py** and it publishes velocity commands in order to move TIAGo and also target position to be reached through move base action. It contains also subscribers' callback functions. For further informations related to base teleoperation see **Chapter 4**.

* **image_publisher.py** is not used for our purpose. It is simply a publisher via TCP/IP communication of the information acquired from TIAGo RGB-D camera.

* **image_server_TCP.py** is the script that receive the information published from **image_publisher.py** 

* **server_socket.py** has been already described. It is the first script to launch in order to wait client request connection.

* **teleoperate_arm.py** is the script demanded to teleoperate TIAGo arm. In particular it defines a class to store variables, methods, subscribers and publishers.
  It contains also subscribers' callback function. For further informations related to TIAGo arm teleoperation see **Chapter 5**.
  

