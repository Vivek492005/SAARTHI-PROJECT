#ifndef CC_EVENT_CHANNEL
#define CC_EVENT_CHANNEL

#include "EventProcessor.h"

template <typename ControllerType, typename StateValues> 
void EventChannel<ControllerType, StateValues>::notify(){
    // cehck if channel event buffer is empty
    if(eventBuffer.empty()){
        printf("[ERROR][EventProcessor:channel] notify - event buffer empty\n");
        return;
    }

    // get event from channel event buffer
    Event<StateValues> event = eventBuffer.front();
    eventBuffer.pop();

    // set state and notify to controllers
    for(int i = 0; i < controllers.size(); i++){
        controllers[i].setState(event.getStateName(), event.getStateValue());
        controllers[i].execute();
    }
}

#endif