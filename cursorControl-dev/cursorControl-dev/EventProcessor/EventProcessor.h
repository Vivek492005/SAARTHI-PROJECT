#ifndef CC_EVENT_PROCESSOR
#define CC_EVENT_PROCESSOR

#include "Controller\Controller.h"
#include "InputBuffer\InputBuffer.h"
#include "Detector\Detector.h"
#include "opencv2\core\mat.hpp"
#include "opencv2\core\types.hpp"

#include <vector>

// class for event
template <typename StateValues>
class Event{
    StateNames stateName;
    ControllerStateValue<StateValues> stateValue;

    public:
        void setStateName(StateNames name){ stateName = name; }
        void setStateValue(ControllerStateValue<StateValues> value){ stateValue = value; }
        StateNames getStateName(){ return stateName; }
        ControllerStateValue<StateValues> getStateValue(){ return stateValue; }
};

// base class for event channel
template <typename ControllerType, typename StateValues>
class EventChannel{
    std::vector<ControllerType> controllers;
    std::queue<Event<StateValues>> eventBuffer;

    public:
        void attach(ControllerType controller){ controllers.push_back(controller); };
        void pushEvent(Event<StateValues> event){ eventBuffer.push(event); };
        void notify();
};

// class for mouse mover event channel
class MouseMoverEventChannel : public EventChannel<MouseMover, Position>{};

// class for mouse clicker event channel
class MouseClickerEventChannel : public EventChannel<MouseClicker, ClickStates>{};

// base class for event generator
template <typename InputBufferType, typename ControllerType, typename StateValues>
class EventGenerator{
    InputBufferType* inputBuffer;  
    EventChannel<ControllerType, StateValues>* eventChannel;

    public:
        EventGenerator(){}
        void setInputBuffer( InputBufferType* buffer ){ inputBuffer = buffer; }
        void setEventChannel(EventChannel<ControllerType, StateValues>* channel){ eventChannel = channel; }
        InputBufferType* getInputBuffer(){ return inputBuffer; }
        EventChannel<ControllerType, StateValues>* getEventChannel(){ return eventChannel; }
        virtual void run() = 0;
};

// class for mouse mover event generator
class MouseMoverEventGenerator : public EventGenerator<VideoInputBuffer, MouseMover, Position>{
    cv::Mat faceTemplate;
    public:
        MouseMoverEventGenerator(){}
        MouseMoverEventGenerator(cv::Mat face){ faceTemplate = face; }
        void setFaceTemplate(cv::Mat face){ faceTemplate = face; }
        void run();
};

// class for mouse clicker event generator
class MouseClickerEventGenerator : public EventGenerator<VideoInputBuffer, MouseClicker, ClickStates>{
    public:
        void run();
};

#endif