#ifndef CC_MOUSE_CONTROLLER
#define CC_MOUSE_CONTROLLER

#include "Controller.h"

#include <windows.h>

MouseController::MouseController(){
    // StateNames mousePosition = mouse_position;
    Position position;
    setState(StateNames::mouse_position, ControllerStateValue<Position>(position));
    
    // StateNames mouseClickState = mouse_click_state;
    ClickStates clickState{};
    setState(StateNames::mouse_click_state, ControllerStateValue<ClickStates>(clickState));
}

void MouseMover::execute(){
    // get mouse position
    ControllerStateValue<Position> mouseMoveState = getState<ControllerStateValue<Position>>(StateNames::mouse_position);
    Position position = mouseMoveState.value();

    // create an mouse input event
    INPUT Input = {0};
    Input.type = INPUT_MOUSE;
    Input.mi.dwFlags = MOUSEEVENTF_MOVE|MOUSEEVENTF_ABSOLUTE;

    // move mouse cursor
    Input.mi.dx = LONG(position.x);
    Input.mi.dy = LONG(position.y);
    SendInput(1,&Input,sizeof(INPUT));

    // set input event to zero - TODO delete INPUT
    ZeroMemory(&Input,sizeof(INPUT));
}

void MouseClicker::execute(){
    // get click state
    ControllerStateValue<ClickStates> mouseClickState = getState<ControllerStateValue<ClickStates>>(StateNames::mouse_click_state);
    ClickStates clickState = mouseClickState.value();

    // create and mouse input event
    INPUT Input = {0};
    Input.type = INPUT_MOUSE;

    if(clickState == ClickStates::Right){
        // hold down mouse right button
        Input.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN;
        SendInput(1,&Input,sizeof(INPUT));

        // release mouse right button
        Input.mi.dwFlags = MOUSEEVENTF_RIGHTUP;
        SendInput(1,&Input,sizeof(INPUT));
    }
    else if(clickState == ClickStates::Left){
        // hold down mouse left button
        Input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
        SendInput(1,&Input,sizeof(INPUT));

        // release mouse left button 
        Input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
        SendInput(1,&Input,sizeof(INPUT));
    }
    else{
        printf("[DEBUG][Controller:mousectl] MouseClicker - No actionable click state\n");
    }

    // set input event to zero - TODO delete INPUT
    ZeroMemory(&Input,sizeof(INPUT));
}

#endif