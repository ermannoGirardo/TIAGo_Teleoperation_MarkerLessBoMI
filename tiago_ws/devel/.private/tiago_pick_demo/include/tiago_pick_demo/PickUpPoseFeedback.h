// Generated by gencpp from file tiago_pick_demo/PickUpPoseFeedback.msg
// DO NOT EDIT!


#ifndef TIAGO_PICK_DEMO_MESSAGE_PICKUPPOSEFEEDBACK_H
#define TIAGO_PICK_DEMO_MESSAGE_PICKUPPOSEFEEDBACK_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace tiago_pick_demo
{
template <class ContainerAllocator>
struct PickUpPoseFeedback_
{
  typedef PickUpPoseFeedback_<ContainerAllocator> Type;

  PickUpPoseFeedback_()
    {
    }
  PickUpPoseFeedback_(const ContainerAllocator& _alloc)
    {
  (void)_alloc;
    }







  typedef boost::shared_ptr< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> const> ConstPtr;

}; // struct PickUpPoseFeedback_

typedef ::tiago_pick_demo::PickUpPoseFeedback_<std::allocator<void> > PickUpPoseFeedback;

typedef boost::shared_ptr< ::tiago_pick_demo::PickUpPoseFeedback > PickUpPoseFeedbackPtr;
typedef boost::shared_ptr< ::tiago_pick_demo::PickUpPoseFeedback const> PickUpPoseFeedbackConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >::stream(s, "", v);
return s;
}


} // namespace tiago_pick_demo

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsFixedSize< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
{
  static const char* value()
  {
    return "d41d8cd98f00b204e9800998ecf8427e";
  }

  static const char* value(const ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xd41d8cd98f00b204ULL;
  static const uint64_t static_value2 = 0xe9800998ecf8427eULL;
};

template<class ContainerAllocator>
struct DataType< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
{
  static const char* value()
  {
    return "tiago_pick_demo/PickUpPoseFeedback";
  }

  static const char* value(const ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
{
  static const char* value()
  {
    return "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======\n"
"#feedback\n"
"\n"
;
  }

  static const char* value(const ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream&, T)
    {}

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct PickUpPoseFeedback_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream&, const std::string&, const ::tiago_pick_demo::PickUpPoseFeedback_<ContainerAllocator>&)
  {}
};

} // namespace message_operations
} // namespace ros

#endif // TIAGO_PICK_DEMO_MESSAGE_PICKUPPOSEFEEDBACK_H
