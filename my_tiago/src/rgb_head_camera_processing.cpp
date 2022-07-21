// C++ standard headers
#include <exception>
#include <string>

// Boost headers
#include <boost/shared_ptr.hpp>

// ROS headers
#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <actionlib/client/simple_action_client.h>
#include <sensor_msgs/CameraInfo.h>
#include <geometry_msgs/PointStamped.h>
#include <control_msgs/PointHeadAction.h>
#include <sensor_msgs/image_encodings.h>
#include <ros/topic.h>

// OpenCV headers
#include <opencv2/highgui/highgui.hpp>
#include <cv_bridge/cv_bridge.h>
#include "opencv2/imgproc/imgproc.hpp"
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

static const std::string windowName      = "Inside of TIAGo's head";
static const std::string cameraFrame     = "/xtion_rgb_optical_frame";
static const std::string imageTopic      = "/xtion/rgb/image_raw";
static const std::string cameraInfoTopic = "/xtion/rgb/camera_info";
static const std::string imagePublisherTopic = "/processed_image";


// Intrinsic parameters of the camera
cv::Mat cameraIntrinsics;

//subscriber to imageTopic
//image_transport::Subscriber sub;

//publisher to imagePublisherTopic
image_transport::Publisher pub;
ros::Publisher img_pub;

//Publisher to republish to use it in a python script
ros::Publisher republisher;

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// ROS call back for every new image received
void imageCallback(const sensor_msgs::ImageConstPtr& imgMsg)
{
    cv_bridge::CvImagePtr cvImgPtr;

    cvImgPtr = cv_bridge::toCvCopy(imgMsg, sensor_msgs::image_encodings::BGR8);
    

    sensor_msgs::ImagePtr msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", cvImgPtr->image).toImageMsg();

    pub.publish(msg);

}

void imageRepublishCallback(const sensor_msgs::ImageConstPtr& imgMsg)
{
    sensor_msgs::CompressedImage img_msg;
    img_msg.data = imgMsg ->data;
    republisher.publish(img_msg);
}

// Entry point
int main(int argc, char** argv)
{

    //Init the ROS node
    ros::init(argc,argv,"rgb_head_image_processing");

    ROS_INFO("Starting rgb_head_image_processing application...");

    ros::NodeHandle nh;

    if (!ros::Time::waitForValid(ros::WallDuration(10.0))) // NOTE: Important when using simulated clock
    {
        ROS_FATAL("Timed-out waiting for valid time.");
        return EXIT_FAILURE;
    }

    // Get the camera intrinsic parameters from the appropriate ROS topic
    ROS_INFO("Waiting for camera intrinsics ... ");
    sensor_msgs::CameraInfoConstPtr msg = ros::topic::waitForMessage
      <sensor_msgs::CameraInfo>(cameraInfoTopic, ros::Duration(10.0));
    if(msg.use_count() > 0)
    {
        cameraIntrinsics = cv::Mat::zeros(3,3,CV_64F);
        cameraIntrinsics.at<double>(0, 0) = msg->K[0]; //fx
        cameraIntrinsics.at<double>(1, 1) = msg->K[4]; //fy
        cameraIntrinsics.at<double>(0, 2) = msg->K[2]; //cx
        cameraIntrinsics.at<double>(1, 2) = msg->K[5]; //cy
        cameraIntrinsics.at<double>(2, 2) = 1;
    }

    // Define ROS topic from where TIAGo publishes images
    image_transport::ImageTransport it(nh);

    // use compressed image transport to use less network bandwidth
    image_transport::TransportHints transportHint("compressed");

    //declare a subscriber listen on imageTopic and its relative callback
    image_transport::Subscriber sub = it.subscribe(imageTopic, 1, imageCallback,transportHint);

    //declare a subscriber listen on imagePublisherTopic in order to republish (in order to use it in a python script)
    image_transport::Subscriber sub_republish = it.subscribe(imagePublisherTopic,1,imageRepublishCallback,transportHint);

    republisher = nh.advertise<sensor_msgs::CompressedImage>("/processed_image/republish",1000);

    pub = it.advertise(imagePublisherTopic, 1);


    //enter a loop that processes ROS callbacks. Press CTRL+C to exit the loop
    ros::spin();

    return EXIT_SUCCESS;
}