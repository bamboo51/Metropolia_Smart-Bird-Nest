#include "streamer.h"
#include "camera.h"
#include <Poco/Net/HTTPServer.h>
#include <Poco/Net/HTTPRequestHandler.h>
#include <Poco/Net/HTTPRequestHandlerFactory.h>
#include <Poco/Net/HTTPServerParams.h>
#include <Poco/Net/ServerSocket.h>
#include <Poco/ThreadPool.h>
#include <iostream>

// MJPEG frame boundary string
const std::string boundary = "--frameboundary\r\n";

// Class to handle MJPEG stream requests
class MJPEGRequestHandler : public Poco::Net::HTTPRequestHandler {
public:
    void handleRequest(Poco::Net::HTTPServerRequest& request, Poco::Net::HTTPServerResponse& response) override {
        Camera camera;
        camera.start();
        response.setContentType("multipart/x-mixed-replace; boundary=" + boundary);
        std::ostream& ostr = response.send();
        camera.streamMJPEG(ostr);
        camera.stop();
    }
};

// Factory to create request handlers for HTTP requests
class MJPEGRequestHandlerFactory : public Poco::Net::HTTPRequestHandlerFactory {
public:
    Poco::Net::HTTPRequestHandler* createRequestHandler(const Poco::Net::HTTPServerRequest& request) override {
        return new MJPEGRequestHandler();
    }
};

// Function to start the HTTP server
void startWebServer(int port) {
    Poco::Net::ServerSocket socket(port);  // Bind to the port
    Poco::Net::HTTPServer server(new MJPEGRequestHandlerFactory(), socket, new Poco::Net::HTTPServerParams);
    std::cout << "Server started on port " << port << std::endl;
    server.start();  // Start the server
    while (true);    // Keep the server running
}