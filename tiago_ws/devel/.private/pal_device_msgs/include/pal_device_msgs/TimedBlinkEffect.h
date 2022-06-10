// Generated by gencpp from file pal_device_msgs/TimedBlinkEffect.msg
// DO NOT EDIT!


#ifndef PAL_DEVICE_MSGS_MESSAGE_TIMEDBLINKEFFECT_H
#define PAL_DEVICE_MSGS_MESSAGE_TIMEDBLINKEFFECT_H

#include <ros/service_traits.h>


#include <pal_device_msgs/TimedBlinkEffectRequest.h>
#include <pal_device_msgs/TimedBlinkEffectResponse.h>


namespace pal_device_msgs
{

struct TimedBlinkEffect
{

typedef TimedBlinkEffectRequest Request;
typedef TimedBlinkEffectResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;

}; // struct TimedBlinkEffect
} // namespace pal_device_msgs


namespace ros
{
namespace service_traits
{


template<>
struct MD5Sum< ::pal_device_msgs::TimedBlinkEffect > {
  static const char* value()
  {
    return "79f0d7fa42ad812456d328f694635ba8";
  }

  static const char* value(const ::pal_device_msgs::TimedBlinkEffect&) { return value(); }
};

template<>
struct DataType< ::pal_device_msgs::TimedBlinkEffect > {
  static const char* value()
  {
    return "pal_device_msgs/TimedBlinkEffect";
  }

  static const char* value(const ::pal_device_msgs::TimedBlinkEffect&) { return value(); }
};


// service_traits::MD5Sum< ::pal_device_msgs::TimedBlinkEffectRequest> should match
// service_traits::MD5Sum< ::pal_device_msgs::TimedBlinkEffect >
template<>
struct MD5Sum< ::pal_device_msgs::TimedBlinkEffectRequest>
{
  static const char* value()
  {
    return MD5Sum< ::pal_device_msgs::TimedBlinkEffect >::value();
  }
  static const char* value(const ::pal_device_msgs::TimedBlinkEffectRequest&)
  {
    return value();
  }
};

// service_traits::DataType< ::pal_device_msgs::TimedBlinkEffectRequest> should match
// service_traits::DataType< ::pal_device_msgs::TimedBlinkEffect >
template<>
struct DataType< ::pal_device_msgs::TimedBlinkEffectRequest>
{
  static const char* value()
  {
    return DataType< ::pal_device_msgs::TimedBlinkEffect >::value();
  }
  static const char* value(const ::pal_device_msgs::TimedBlinkEffectRequest&)
  {
    return value();
  }
};

// service_traits::MD5Sum< ::pal_device_msgs::TimedBlinkEffectResponse> should match
// service_traits::MD5Sum< ::pal_device_msgs::TimedBlinkEffect >
template<>
struct MD5Sum< ::pal_device_msgs::TimedBlinkEffectResponse>
{
  static const char* value()
  {
    return MD5Sum< ::pal_device_msgs::TimedBlinkEffect >::value();
  }
  static const char* value(const ::pal_device_msgs::TimedBlinkEffectResponse&)
  {
    return value();
  }
};

// service_traits::DataType< ::pal_device_msgs::TimedBlinkEffectResponse> should match
// service_traits::DataType< ::pal_device_msgs::TimedBlinkEffect >
template<>
struct DataType< ::pal_device_msgs::TimedBlinkEffectResponse>
{
  static const char* value()
  {
    return DataType< ::pal_device_msgs::TimedBlinkEffect >::value();
  }
  static const char* value(const ::pal_device_msgs::TimedBlinkEffectResponse&)
  {
    return value();
  }
};

} // namespace service_traits
} // namespace ros

#endif // PAL_DEVICE_MSGS_MESSAGE_TIMEDBLINKEFFECT_H
