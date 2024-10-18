#include "camera.h"
#include <opencv2/opencv.hpp>
#include <Poco/Thread.h>
#include <vector>
#include <iostream>

// Function to initialize and start the camera
void Camera::start() {
    cap.open(0);  // Open the default camera (Raspberry Pi Camera)
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera" << std::endl;
        return;
    }
    std::cout << "Camera started successfully" << std::endl;
}

// Function to stop the camera
void Camera::stop() {
    cap.release();
    std::cout << "Camera stopped." << std::endl;
}

// Function to capture a single frame from the camera
bool Camera::captureFrame(cv::Mat& frame) {
    if (cap.isOpened()) {
        cap >> frame;  // Capture frame from camera
        if (frame.empty()) {
            std::cerr << "Error: Captured an empty frame" << std::endl;
            return false;
        }
        return true;
    }
    return false;
}

// Function to generate MJPEG stream
void Camera::streamMJPEG(std::ostream& outputStream) {
    std::vector<uchar> buff;
    std::vector<int> param = {cv::IMWRITE_JPEG_QUALITY, 90};  // JPEG quality settings
    cv::Mat frame;

    while (true) {
        if (!captureFrame(frame)) break;  // If capturing fails, exit the loop

        // Encode frame as JPEG
        cv::imencode(".jpg", frame, buff, param);

        // Send the frame in MJPEG format
        outputStream << "--frameboundary\r\n";
        outputStream << "Content-Type: image/jpeg\r\n";
        outputStream << "Content-Length: " << buff.size() << "\r\n\r\n";
        outputStream.write(reinterpret_cast<const char*>(buff.data()), buff.size());
        outputStream << "\r\n";
        outputStream.flush();

        // Sleep briefly to control frame rate
        Poco::Thread::sleep(50);  // Adjust for desired frame rate
    }
}
