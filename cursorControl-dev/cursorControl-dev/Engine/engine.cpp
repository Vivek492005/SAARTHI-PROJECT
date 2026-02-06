#ifndef CC_ENGINE_CPP
#define CC_ENGINE_CPP

#include "Engine.h"
#include <iostream>
#include <iomanip>

MouseEngine::MouseEngine(int period, int numWakeUps){
    // set engine properties
    setPeriod(period);
    setNumWakeUps(numWakeUps);
    setStartTime(std::chrono::system_clock::now());

    // get a frame from input device
	videoInputBuffer.capture();
	cv::Mat frame = videoInputBuffer.get();

    // detect face for the user
	cv::Rect face = faceDetector.detect(1, frame);
	if(face.empty()){
		printf("[ERROR][Engine:engine] MouseEngine - face detector returned empty rectangle\n");
		return;
	}

	// TEMP - show elipse on face
	cv::Point center;
	center.x = face.x + face.width / 2;
	center.y = face.y + face.height / 2;
	cv::ellipse(frame, center, cv::Size(face.width / 2, face.height / 2), 0, 0, 360, cv::Scalar(255, 0, 255), 4, 8, 0);
	cv::imshow ("Face detection", frame);
    cv::waitKey();

	cv::Mat faceTemplate(frame, face);
    this->faceTemplate = faceTemplate;

    // configure event and generator
    mouseMoverEventChannel.attach(mouseMover);
	mouseMoverEventGenerator.setFaceTemplate(faceTemplate);
	mouseMoverEventGenerator.setInputBuffer(&videoInputBuffer);
	mouseMoverEventGenerator.setEventChannel(&mouseMoverEventChannel);
}

void MouseEngine::runTask(){
    int numWakeUps = getNumWakeUps();
    int decrement = numWakeUps == 0 ? 0 : 1;
    std::chrono::milliseconds period = getPeriod();

    while(numWakeUps){
        // get current time
        std::chrono::system_clock::time_point currentTime = std::chrono::system_clock::now();

        // print current time for debug purpose
        // std::time_t now = std::chrono::system_clock::to_time_t(currentTime);
        // std::cout << "[DEBUG][Engine:engine] runTask - current time " << std::put_time(std::localtime(&now), "%F %T") << std::endl;

        // move cursor
        moveCursor();
        
        // decrement counter and go to sleep
        numWakeUps -= decrement;
        std::this_thread::sleep_until(currentTime + period);
    }
}

void MouseEngine::moveCursor(){
    // run the event generator
	videoInputBuffer.capture();
	mouseMoverEventGenerator.run();
}

#endif