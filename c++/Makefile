CXX = g++
CXXFLAGS = -std=c++11 -lpoco_net -lpoco_util -lpoco_foundation -lopencv_core -lopencv_highgui -lopencv_imgcodecs -lopencv_videoio -lwiringPi

TARGET = bird_nest_streamer
SRC = main.cpp video_streamer.cpp sensor.cpp camera.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)
