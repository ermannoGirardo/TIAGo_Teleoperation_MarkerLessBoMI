execute_process(COMMAND "/home/ermanno/tiago_public_ws/build/pal_navigation_sm/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/ermanno/tiago_public_ws/build/pal_navigation_sm/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
