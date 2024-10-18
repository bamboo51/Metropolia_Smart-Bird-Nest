#ifndef CAMERA_H
#define CAMERA_H

#include <opencv2/opencv.hpp>
#include <ostream>

class Camera {
public:
    void start();  // Start the camera
    void stop();   // Stop the camera
    bool captureFrame(cv::Mat& frame);  // Capture a single frame
    void streamMJPEG(std::ostream& outputStream);  // Stream frames as MJPEG
private:
    cv::VideoCapture cap;
};

#endif // CAMERA_H
