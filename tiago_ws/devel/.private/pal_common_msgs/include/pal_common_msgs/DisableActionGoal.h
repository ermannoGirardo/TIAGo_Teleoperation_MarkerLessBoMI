// Generated by gencpp from file pal_common_msgs/DisableActionGoal.msg
// DO NOT EDIT!


#ifndef PAL_COMMON_MSGS_MESSAGE_DISABLEACTIONGOAL_H
#define PAL_COMMON_MSGS_MESSAGE_DISABLEACTIONGOAL_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <std_msgs/Header.h>
#include <actionlib_msgs/GoalID.h>
#include <pal_common_msgs/DisableGoal.h>

namespace pal_common_msgs
{
template <class ContainerAllocator>
struct DisableActionGoal_
{
  typedef DisableActionGoal_<ContainerAllocator> Type;

  DisableActionGoal_()
    : header()
    , goal_id()
    , goal()  {
    }
  DisableActionGoal_(const ContainerAllocator& _alloc)
    : header(_alloc)
    , goal_id(_alloc)
    , goal(_alloc)  {
  (void)_alloc;
    }



   typedef  ::std_msgs::Header_<ContainerAllocator>  _header_type;
  _header_type header;

   typedef  ::actionlib_msgs::GoalID_<ContainerAllocator>  _goal_id_type;
  _goal_id_type goal_id;

   typedef  ::pal_common_msgs::DisableGoal_<ContainerAllocator>  _goal_type;
  _goal_type goal;





  typedef boost::shared_ptr< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> const> ConstPtr;

}; // struct DisableActionGoal_

typedef ::pal_common_msgs::DisableActionGoal_<std::allocator<void> > DisableActionGoal;

typedef boost::shared_ptr< ::pal_common_msgs::DisableActionGoal > DisableActionGoalPtr;
typedef boost::shared_ptr< ::pal_common_msgs::DisableActionGoal const> DisableActionGoalConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator1> & lhs, const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator2> & rhs)
{
  return lhs.header == rhs.header &&
    lhs.goal_id == rhs.goal_id &&
    lhs.goal == rhs.goal;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator1> & lhs, const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace pal_common_msgs

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsFixedSize< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct IsMessage< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> const>
  : TrueType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
{
  static const char* value()
  {
    return "a7386e7a41cdfb8807af810188ae810d";
  }

  static const char* value(const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xa7386e7a41cdfb88ULL;
  static const uint64_t static_value2 = 0x07af810188ae810dULL;
};

template<class ContainerAllocator>
struct DataType< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
{
  static const char* value()
  {
    return "pal_common_msgs/DisableActionGoal";
  }

  static const char* value(const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
{
  static const char* value()
  {
    return "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======\n"
"\n"
"Header header\n"
"actionlib_msgs/GoalID goal_id\n"
"DisableGoal goal\n"
"\n"
"================================================================================\n"
"MSG: std_msgs/Header\n"
"# Standard metadata for higher-level stamped data types.\n"
"# This is generally used to communicate timestamped data \n"
"# in a particular coordinate frame.\n"
"# \n"
"# sequence ID: consecutively increasing ID \n"
"uint32 seq\n"
"#Two-integer timestamp that is expressed as:\n"
"# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')\n"
"# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')\n"
"# time-handling sugar is provided by the client library\n"
"time stamp\n"
"#Frame this data is associated with\n"
"string frame_id\n"
"\n"
"================================================================================\n"
"MSG: actionlib_msgs/GoalID\n"
"# The stamp should store the time at which this goal was requested.\n"
"# It is used by an action server when it tries to preempt all\n"
"# goals that were requested before a certain time\n"
"time stamp\n"
"\n"
"# The id provides a way to associate feedback and\n"
"# result message with specific goal requests. The id\n"
"# specified must be unique.\n"
"string id\n"
"\n"
"\n"
"================================================================================\n"
"MSG: pal_common_msgs/DisableGoal\n"
"# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======\n"
"# This action disables a functionality for a set amount of seconds.\n"
"# A negative or zero value will disable it until the goal is canceled\n"
"\n"
"float32 duration # [s] for how long to disable the functionality\n"
;
  }

  static const char* value(const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.header);
      stream.next(m.goal_id);
      stream.next(m.goal);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct DisableActionGoal_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::pal_common_msgs::DisableActionGoal_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::pal_common_msgs::DisableActionGoal_<ContainerAllocator>& v)
  {
    s << indent << "header: ";
    s << std::endl;
    Printer< ::std_msgs::Header_<ContainerAllocator> >::stream(s, indent + "  ", v.header);
    s << indent << "goal_id: ";
    s << std::endl;
    Printer< ::actionlib_msgs::GoalID_<ContainerAllocator> >::stream(s, indent + "  ", v.goal_id);
    s << indent << "goal: ";
    s << std::endl;
    Printer< ::pal_common_msgs::DisableGoal_<ContainerAllocator> >::stream(s, indent + "  ", v.goal);
  }
};

} // namespace message_operations
} // namespace ros

#endif // PAL_COMMON_MSGS_MESSAGE_DISABLEACTIONGOAL_H
