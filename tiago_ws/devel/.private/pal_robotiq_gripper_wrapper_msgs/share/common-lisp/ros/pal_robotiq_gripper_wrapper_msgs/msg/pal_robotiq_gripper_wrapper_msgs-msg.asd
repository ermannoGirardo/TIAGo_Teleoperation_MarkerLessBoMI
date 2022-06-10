
(cl:in-package :asdf)

(defsystem "pal_robotiq_gripper_wrapper_msgs-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :std_msgs-msg
)
  :components ((:file "_package")
    (:file "GripperStatus" :depends-on ("_package_GripperStatus"))
    (:file "_package_GripperStatus" :depends-on ("_package"))
  ))