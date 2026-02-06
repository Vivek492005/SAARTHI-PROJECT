#ifndef CC_CONTROLLER
#define CC_CONTROLLER

#include "boost\variant.hpp"

#include <utility>
#include <string>
#include <map>

// enum for controller state names
enum class StateNames{
    mouse_position,
    mouse_click_state
};

// enum for mouse click states
enum class ClickStates{ None, Right, Left };

// class to hold position such as mouse cursor
class Position{
    public:
        int x;
        int y;
        Position() { x = -1; y = -1; }
        Position(int x_p, int y_p) { x = x_p; y = y_p; }
};

// template class to create controller state value
template <typename StateValue>
class ControllerStateValue{
    StateValue stateValue;
    public:
        ControllerStateValue() {};
        ControllerStateValue(StateValue value) : stateValue(value) {};
        StateValue value() { return stateValue; };
};

// typedef of controller state value types 
typedef boost::variant<ControllerStateValue<Position>,ControllerStateValue<ClickStates>> StateValues; 

// base class for contorller
class Controller {
    std::map< StateNames, StateValues > states;
    public:
        template <typename StateValue> void setState(StateNames stateName, StateValue stateValue){ states[stateName] = stateValue; }
        template <typename StateValue> StateValue getState(StateNames name){ return boost::get<StateValue>(states[name]); }
        virtual void execute() = 0;
};

// base class for mouse event processor
class MouseController : public Controller {
    public:
        MouseController();
        virtual void execute() = 0;
};

// class for mouse movement event processor 
class MouseMover : public MouseController {
    public:
        void execute();
};

// class for mouse click event processor 
class MouseClicker : public MouseController {
    public:
        void execute();
};

#endif