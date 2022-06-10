// Generated by gencpp from file pal_detection_msgs/StopEnrollment.msg
// DO NOT EDIT!


#ifndef PAL_DETECTION_MSGS_MESSAGE_STOPENROLLMENT_H
#define PAL_DETECTION_MSGS_MESSAGE_STOPENROLLMENT_H

#include <ros/service_traits.h>


#include <pal_detection_msgs/StopEnrollmentRequest.h>
#include <pal_detection_msgs/StopEnrollmentResponse.h>


namespace pal_detection_msgs
{

struct StopEnrollment
{

typedef StopEnrollmentRequest Request;
typedef StopEnrollmentResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;

}; // struct StopEnrollment
} // namespace pal_detection_msgs


namespace ros
{
namespace service_traits
{


template<>
struct MD5Sum< ::pal_detection_msgs::StopEnrollment > {
  static const char* value()
  {
    return "fb84ca50753c7bbc7737a1c5095dac61";
  }

  static const char* value(const ::pal_detection_msgs::StopEnrollment&) { return value(); }
};

template<>
struct DataType< ::pal_detection_msgs::StopEnrollment > {
  static const char* value()
  {
    return "pal_detection_msgs/StopEnrollment";
  }

  static const char* value(const ::pal_detection_msgs::StopEnrollment&) { return value(); }
};


// service_traits::MD5Sum< ::pal_detection_msgs::StopEnrollmentRequest> should match
// service_traits::MD5Sum< ::pal_detection_msgs::StopEnrollment >
template<>
struct MD5Sum< ::pal_detection_msgs::StopEnrollmentRequest>
{
  static const char* value()
  {
    return MD5Sum< ::pal_detection_msgs::StopEnrollment >::value();
  }
  static const char* value(const ::pal_detection_msgs::StopEnrollmentRequest&)
  {
    return value();
  }
};

// service_traits::DataType< ::pal_detection_msgs::StopEnrollmentRequest> should match
// service_traits::DataType< ::pal_detection_msgs::StopEnrollment >
template<>
struct DataType< ::pal_detection_msgs::StopEnrollmentRequest>
{
  static const char* value()
  {
    return DataType< ::pal_detection_msgs::StopEnrollment >::value();
  }
  static const char* value(const ::pal_detection_msgs::StopEnrollmentRequest&)
  {
    return value();
  }
};

// service_traits::MD5Sum< ::pal_detection_msgs::StopEnrollmentResponse> should match
// service_traits::MD5Sum< ::pal_detection_msgs::StopEnrollment >
template<>
struct MD5Sum< ::pal_detection_msgs::StopEnrollmentResponse>
{
  static const char* value()
  {
    return MD5Sum< ::pal_detection_msgs::StopEnrollment >::value();
  }
  static const char* value(const ::pal_detection_msgs::StopEnrollmentResponse&)
  {
    return value();
  }
};

// service_traits::DataType< ::pal_detection_msgs::StopEnrollmentResponse> should match
// service_traits::DataType< ::pal_detection_msgs::StopEnrollment >
template<>
struct DataType< ::pal_detection_msgs::StopEnrollmentResponse>
{
  static const char* value()
  {
    return DataType< ::pal_detection_msgs::StopEnrollment >::value();
  }
  static const char* value(const ::pal_detection_msgs::StopEnrollmentResponse&)
  {
    return value();
  }
};

} // namespace service_traits
} // namespace ros

#endif // PAL_DETECTION_MSGS_MESSAGE_STOPENROLLMENT_H
