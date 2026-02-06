#ifndef CC_EVENT_GENERATOR
#define CC_EVENT_GENERATOR

#include "EventProcessor.h"
#include "channel.cpp"

void MouseMoverEventGenerator::run(){
    // get input from video input buffer
    VideoInputBuffer* videoInputBuffer = getInputBuffer();
    cv::Mat input = videoInputBuffer->get();

    // check if input is empty
    if(input.empty()){
        printf("[ERROR][EventProcessor:generator] run - input is empty\n");
        return;
    }

    // detect face location
    CVTemplateFaceDetector faceDetector;
    cv::Point faceLocation = faceDetector.detect(2, input, faceTemplate);

    // get mouse postion relative to screen
    int x = faceLocation.x * (65535.0 / input.rows);
    int y = faceLocation.y * (65535.0 / input.cols);
    
    // print mouse position conversion for debug purpose
    // printf("[DEBUG][EventProcessor:genarator] run - mouse position conversion %d %d (%d %d) >> %d %d\n", faceLocation.x, faceLocation.y, input.rows, input.cols, x, y);

    // create an controller event
    Event<Position> event;
    Position position(x, y);
    event.setStateName(StateNames::mouse_position);
    event.setStateValue(ControllerStateValue<Position>(position));

    // push the event to event channel
    EventChannel<MouseMover, Position>* eventChannel = getEventChannel();
    eventChannel->pushEvent(event);

    // notify the controllers
    eventChannel->notify();
}

void MouseClickerEventGenerator::run(){
    // get input from video input buffer
    VideoInputBuffer* videoInputBuffer = getInputBuffer();
    cv::Mat input = videoInputBuffer->get();

    // check if input is empty
    if(input.empty()){
        printf("[ERROR][EventProcessor:generator] run - input is empty\n");
        return;
    }

    // create an controller event 
    Event<ClickStates> event;
    event.setStateName(StateNames::mouse_click_state);
    event.setStateValue(ControllerStateValue<ClickStates>(ClickStates::Right));

    // push the event to event channel
    EventChannel<MouseClicker, ClickStates>* eventChannel = getEventChannel();
    eventChannel->pushEvent(event);

    // notify the controllers
    eventChannel->notify();
}

#endif