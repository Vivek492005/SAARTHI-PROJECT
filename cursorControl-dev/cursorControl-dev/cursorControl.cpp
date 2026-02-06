// should try 0x501 below instead of 0x500 if we run into error
#define _WIN32_WINNT 0x500

#include "cursorControl.h"
#include "Controller\Controller.h"
#include "InputBuffer\InputBuffer.h"
#include "EventProcessor\EventProcessor.h"
#include "Detector\Detector.h"
#include "Engine\Engine.h"
#include "opencv2\core\mat.hpp"
#include "opencv2\core\types.hpp"

#include <iostream>
#include <cstdio>
#include <cstring>

using namespace std;

const char* usage = "cursorControl: control devices virtually\n"
				"options:\n"
				"-V, --version\t print version\n"
				"--run\t\t run the program";

int main(int argc, char* argv[]) {
	if(argc != 2){
		printf("%s\n", usage);
		return 1;
	}
	else if (!strcmp(argv[1], "--version") || !strcmp(argv[1], "-V")) {
		printf("%s Version %d.%d.%d\n", argv[0], cursorControl_VERSION_MAJOR, cursorControl_VERSION_MINOR, cursorControl_VERSION_PATCH);
		return 0;
	}
	else if(!strcmp(argv[1], "--run")){
		printf("[INFO][cursorControl:main] starting program ..\n");
	}
	else{
		printf("%s\n", usage);
		return 1;
	}

	MouseEngine mouseEngine(1, 300);
	mouseEngine.runTask();
	return 1;

	// VideoInputBuffer videoInputBuffer;
	// videoInputBuffer.capture();
	// cv::Mat frame = videoInputBuffer.get();

	// CVCascadeFaceDetector faceDetector;
	// // cv::Rect face = faceDetector.detect(frame);
	// cv::Rect face = faceDetector.detect(1, frame);
	// if(face.empty()){
	// 	printf("[ERROR][cursorControl] face detector returned empty rectangle\n");
	// 	return -1;
	// }

	// TEMP - show elipse on face
	// cv::Point center;
	// center.x = face.x + face.width / 2;
	// center.y = face.y + face.height / 2;
	// cv::ellipse(frame, center, cv::Size(face.width / 2, face.height / 2), 0, 0, 360, 
	// 			cv::Scalar(255, 0, 255), 4, 8, 0);
	// cv::imshow ("Face detection", frame);
    // cv::waitKey();

	// cv::Mat faceTemplate(frame, face);

	// MouseMover mouseMover;
	
	// MouseMoverEventChannel mouseMoverEventChannel;
	// mouseMoverEventChannel.attach(mouseMover);
	
	// MouseMoverEventGenerator mouseMoverEventGenerator(faceTemplate);
	// mouseMoverEventGenerator.setInputBuffer(&videoInputBuffer);
	// mouseMoverEventGenerator.setEventChannel(&mouseMoverEventChannel);

	// videoInputBuffer.capture();
	// mouseMoverEventGenerator.run();

	// MouseMover mouseMover;
	// Position position(65535, 123);
	// mouseMover.setState(StateNames::mouse_position, ControllerStateValue<Position>(position));
	// mouseMover.execute();

	// MouseClicker mouseClicker;
	// MouseClickerEventChannel mouseClickerEventChannel;
	// mouseClickerEventChannel.attach(mouseClicker);

	// MouseClickerEventGenerator mouseClickerEventGenerator;
	// mouseClickerEventGenerator.setInputBuffer(&videoInputBuffer);
	// mouseClickerEventGenerator.setEventChannel(&mouseClickerEventChannel);
	
	// videoInputBuffer.capture();
	// mouseClickerEventGenerator.run();

	// MouseClicker mouseClicker;
	// ClickStates clickState = ClickStates::Right;
	// mouseClicker.setState(StateNames::mouse_click_state, ControllerStateValue<ClickStates>(clickState));
	// mouseClicker.execute();

	// VideoInputBuffer videoInput;
	// videoInput.capture();
	// videoInput.show();
}