execute_process(COMMAND "/home/ermanno/tiago_public_ws/build/rqt_joint_trajectory_controller/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/ermanno/tiago_public_ws/build/rqt_joint_trajectory_controller/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
