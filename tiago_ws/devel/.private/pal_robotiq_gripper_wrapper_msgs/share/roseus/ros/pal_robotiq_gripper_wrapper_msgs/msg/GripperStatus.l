;; Auto-generated. Do not edit!


(when (boundp 'pal_robotiq_gripper_wrapper_msgs::GripperStatus)
  (if (not (find-package "PAL_ROBOTIQ_GRIPPER_WRAPPER_MSGS"))
    (make-package "PAL_ROBOTIQ_GRIPPER_WRAPPER_MSGS"))
  (shadow 'GripperStatus (find-package "PAL_ROBOTIQ_GRIPPER_WRAPPER_MSGS")))
(unless (find-package "PAL_ROBOTIQ_GRIPPER_WRAPPER_MSGS::GRIPPERSTATUS")
  (make-package "PAL_ROBOTIQ_GRIPPER_WRAPPER_MSGS::GRIPPERSTATUS"))

(in-package "ROS")
;;//! \htmlinclude GripperStatus.msg.html
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass pal_robotiq_gripper_wrapper_msgs::GripperStatus
  :super ros::object
  :slots (_header _name _position _fingers_distance _effort ))

(defmethod pal_robotiq_gripper_wrapper_msgs::GripperStatus
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:name __name) "")
    ((:position __position) 0.0)
    ((:fingers_distance __fingers_distance) 0.0)
    ((:effort __effort) 0.0)
    )
   (send-super :init)
   (setq _header __header)
   (setq _name (string __name))
   (setq _position (float __position))
   (setq _fingers_distance (float __fingers_distance))
   (setq _effort (float __effort))
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:name
   (&optional __name)
   (if __name (setq _name __name)) _name)
  (:position
   (&optional __position)
   (if __position (setq _position __position)) _position)
  (:fingers_distance
   (&optional __fingers_distance)
   (if __fingers_distance (setq _fingers_distance __fingers_distance)) _fingers_distance)
  (:effort
   (&optional __effort)
   (if __effort (setq _effort __effort)) _effort)
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; string _name
    4 (length _name)
    ;; float64 _position
    8
    ;; float64 _fingers_distance
    8
    ;; float64 _effort
    8
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; string _name
       (write-long (length _name) s) (princ _name s)
     ;; float64 _position
       (sys::poke _position (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;; float64 _fingers_distance
       (sys::poke _fingers_distance (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;; float64 _effort
       (sys::poke _effort (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; string _name
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _name (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; float64 _position
     (setq _position (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;; float64 _fingers_distance
     (setq _fingers_distance (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;; float64 _effort
     (setq _effort (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;;
   self)
  )

(setf (get pal_robotiq_gripper_wrapper_msgs::GripperStatus :md5sum-) "7c6ae793494e3fe189ecbb9a7faf00ed")
(setf (get pal_robotiq_gripper_wrapper_msgs::GripperStatus :datatype-) "pal_robotiq_gripper_wrapper_msgs/GripperStatus")
(setf (get pal_robotiq_gripper_wrapper_msgs::GripperStatus :definition-)
      "Header header

string name
float64 position
float64 fingers_distance # in meters
float64 effort

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

")



(provide :pal_robotiq_gripper_wrapper_msgs/GripperStatus "7c6ae793494e3fe189ecbb9a7faf00ed")


