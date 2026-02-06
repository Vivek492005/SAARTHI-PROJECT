#ifndef CC_ENGINE
#define CC_ENGINE

#include "InputBuffer\InputBuffer.h"
#include "Controller\Controller.h"
#include "EventProcessor\EventProcessor.h"
#include "Detector\Detector.h"
#include "opencv2\core\mat.hpp"
#include "opencv2\core\types.hpp"

#include <chrono>
#include <thread>

// base class for program engine
class Engine{
    const double microsPerClockTick{ 1.0e6 * std::chrono::system_clock::period::num / std::chrono::system_clock::period::den };
    std::chrono::milliseconds period{ 100 };
    std::chrono::system_clock::time_point startTime;
    int32_t numWakeUps;
    public:
        Engine(){}
        void setPeriod(int period){ this->period = std::chrono::milliseconds(period); }
        void setNumWakeUps(int numWakeUps){ this->numWakeUps = numWakeUps; }
        void setStartTime(std::chrono::system_clock::time_point time){ startTime = time; }
        std::chrono::milliseconds getPeriod(){ return period; }
        int32_t getNumWakeUps(){ return numWakeUps; }
        std::chrono::system_clock::time_point getStartTime(){ return startTime; }
        virtual void runTask() = 0;
};

// class for mouse engine
class MouseEngine : public Engine{
    VideoInputBuffer videoInputBuffer;
	CVCascadeFaceDetector faceDetector;
	MouseMoverEventGenerator mouseMoverEventGenerator;
	MouseMoverEventChannel mouseMoverEventChannel;
	MouseMover mouseMover;
    cv::Mat faceTemplate;
    public:
        MouseEngine(int period, int numWakeUps);
        void runTask();
        void moveCursor();
};

#endif