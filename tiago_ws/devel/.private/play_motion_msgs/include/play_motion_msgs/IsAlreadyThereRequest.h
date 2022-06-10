// Generated by gencpp from file play_motion_msgs/IsAlreadyThereRequest.msg
// DO NOT EDIT!


#ifndef PLAY_MOTION_MSGS_MESSAGE_ISALREADYTHEREREQUEST_H
#define PLAY_MOTION_MSGS_MESSAGE_ISALREADYTHEREREQUEST_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace play_motion_msgs
{
template <class ContainerAllocator>
struct IsAlreadyThereRequest_
{
  typedef IsAlreadyThereRequest_<ContainerAllocator> Type;

  IsAlreadyThereRequest_()
    : motion_name()
    , tolerance(0.0)  {
    }
  IsAlreadyThereRequest_(const ContainerAllocator& _alloc)
    : motion_name(_alloc)
    , tolerance(0.0)  {
  (void)_alloc;
    }



   typedef std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other >  _motion_name_type;
  _motion_name_type motion_name;

   typedef float _tolerance_type;
  _tolerance_type tolerance;





  typedef boost::shared_ptr< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> const> ConstPtr;

}; // struct IsAlreadyThereRequest_

typedef ::play_motion_msgs::IsAlreadyThereRequest_<std::allocator<void> > IsAlreadyThereRequest;

typedef boost::shared_ptr< ::play_motion_msgs::IsAlreadyThereRequest > IsAlreadyThereRequestPtr;
typedef boost::shared_ptr< ::play_motion_msgs::IsAlreadyThereRequest const> IsAlreadyThereRequestConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator1> & lhs, const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator2> & rhs)
{
  return lhs.motion_name == rhs.motion_name &&
    lhs.tolerance == rhs.tolerance;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator1> & lhs, const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace play_motion_msgs

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsFixedSize< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct IsMessage< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
{
  static const char* value()
  {
    return "99caf0c415b632c6336d7371da3ff931";
  }

  static const char* value(const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x99caf0c415b632c6ULL;
  static const uint64_t static_value2 = 0x336d7371da3ff931ULL;
};

template<class ContainerAllocator>
struct DataType< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
{
  static const char* value()
  {
    return "play_motion_msgs/IsAlreadyThereRequest";
  }

  static const char* value(const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
{
  static const char* value()
  {
    return "# Checks if the robot joint state matches the first\n"
"# point of a given motion\n"
"#\n"
"# Robot joint positions will be checked against the\n"
"# values found in the motion's first point, given a\n"
"# tolerance.\n"
"# Joints that are not targetted by the given motion\n"
"# will not be considered.\n"
"\n"
"string motion_name\n"
"float32 tolerance   # in radians\n"
;
  }

  static const char* value(const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.motion_name);
      stream.next(m.tolerance);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct IsAlreadyThereRequest_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::play_motion_msgs::IsAlreadyThereRequest_<ContainerAllocator>& v)
  {
    s << indent << "motion_name: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other > >::stream(s, indent + "  ", v.motion_name);
    s << indent << "tolerance: ";
    Printer<float>::stream(s, indent + "  ", v.tolerance);
  }
};

} // namespace message_operations
} // namespace ros

#endif // PLAY_MOTION_MSGS_MESSAGE_ISALREADYTHEREREQUEST_H
