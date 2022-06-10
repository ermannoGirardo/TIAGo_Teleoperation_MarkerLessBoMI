; Auto-generated. Do not edit!


(cl:in-package pal_robotiq_gripper_wrapper_msgs-msg)


;//! \htmlinclude GripperStatus.msg.html

(cl:defclass <GripperStatus> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (name
    :reader name
    :initarg :name
    :type cl:string
    :initform "")
   (position
    :reader position
    :initarg :position
    :type cl:float
    :initform 0.0)
   (fingers_distance
    :reader fingers_distance
    :initarg :fingers_distance
    :type cl:float
    :initform 0.0)
   (effort
    :reader effort
    :initarg :effort
    :type cl:float
    :initform 0.0))
)

(cl:defclass GripperStatus (<GripperStatus>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <GripperStatus>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'GripperStatus)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name pal_robotiq_gripper_wrapper_msgs-msg:<GripperStatus> is deprecated: use pal_robotiq_gripper_wrapper_msgs-msg:GripperStatus instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <GripperStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pal_robotiq_gripper_wrapper_msgs-msg:header-val is deprecated.  Use pal_robotiq_gripper_wrapper_msgs-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'name-val :lambda-list '(m))
(cl:defmethod name-val ((m <GripperStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pal_robotiq_gripper_wrapper_msgs-msg:name-val is deprecated.  Use pal_robotiq_gripper_wrapper_msgs-msg:name instead.")
  (name m))

(cl:ensure-generic-function 'position-val :lambda-list '(m))
(cl:defmethod position-val ((m <GripperStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pal_robotiq_gripper_wrapper_msgs-msg:position-val is deprecated.  Use pal_robotiq_gripper_wrapper_msgs-msg:position instead.")
  (position m))

(cl:ensure-generic-function 'fingers_distance-val :lambda-list '(m))
(cl:defmethod fingers_distance-val ((m <GripperStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pal_robotiq_gripper_wrapper_msgs-msg:fingers_distance-val is deprecated.  Use pal_robotiq_gripper_wrapper_msgs-msg:fingers_distance instead.")
  (fingers_distance m))

(cl:ensure-generic-function 'effort-val :lambda-list '(m))
(cl:defmethod effort-val ((m <GripperStatus>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader pal_robotiq_gripper_wrapper_msgs-msg:effort-val is deprecated.  Use pal_robotiq_gripper_wrapper_msgs-msg:effort instead.")
  (effort m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <GripperStatus>) ostream)
  "Serializes a message object of type '<GripperStatus>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'name))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'name))
  (cl:let ((bits (roslisp-utils:encode-double-float-bits (cl:slot-value msg 'position))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 32) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 40) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 48) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 56) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-double-float-bits (cl:slot-value msg 'fingers_distance))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 32) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 40) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 48) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 56) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-double-float-bits (cl:slot-value msg 'effort))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 32) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 40) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 48) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 56) bits) ostream))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <GripperStatus>) istream)
  "Deserializes a message object of type '<GripperStatus>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'name) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'name) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 32) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 40) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 48) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 56) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'position) (roslisp-utils:decode-double-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 32) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 40) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 48) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 56) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'fingers_distance) (roslisp-utils:decode-double-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 32) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 40) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 48) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 56) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'effort) (roslisp-utils:decode-double-float-bits bits)))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<GripperStatus>)))
  "Returns string type for a message object of type '<GripperStatus>"
  "pal_robotiq_gripper_wrapper_msgs/GripperStatus")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'GripperStatus)))
  "Returns string type for a message object of type 'GripperStatus"
  "pal_robotiq_gripper_wrapper_msgs/GripperStatus")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<GripperStatus>)))
  "Returns md5sum for a message object of type '<GripperStatus>"
  "7c6ae793494e3fe189ecbb9a7faf00ed")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'GripperStatus)))
  "Returns md5sum for a message object of type 'GripperStatus"
  "7c6ae793494e3fe189ecbb9a7faf00ed")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<GripperStatus>)))
  "Returns full string definition for message of type '<GripperStatus>"
  (cl:format cl:nil "Header header~%~%string name~%float64 position~%float64 fingers_distance # in meters~%float64 effort~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'GripperStatus)))
  "Returns full string definition for message of type 'GripperStatus"
  (cl:format cl:nil "Header header~%~%string name~%float64 position~%float64 fingers_distance # in meters~%float64 effort~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <GripperStatus>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     4 (cl:length (cl:slot-value msg 'name))
     8
     8
     8
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <GripperStatus>))
  "Converts a ROS message object to a list"
  (cl:list 'GripperStatus
    (cl:cons ':header (header msg))
    (cl:cons ':name (name msg))
    (cl:cons ':position (position msg))
    (cl:cons ':fingers_distance (fingers_distance msg))
    (cl:cons ':effort (effort msg))
))
