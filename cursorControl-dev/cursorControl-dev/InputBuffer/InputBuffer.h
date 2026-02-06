#ifndef CC_INPUT_BUFFER
#define CC_INPUT_BUFFER

#include "opencv2\core\mat.hpp"
#include "opencv2\highgui.hpp"
#include "opencv2\imgproc.hpp"
#include "opencv2\videoio.hpp"

#include <queue>

// class for input buffer interface
template <typename Input> 
class InputBuffer{
    std::queue<Input> inputBuffer;
    public:
        void put(Input input){ inputBuffer.push(input); }
        Input get();
        virtual void capture() = 0;
};

// class to hold size of frame such as video frame
class FrameSize{
    public:
        int height;
        int width;
};

// class for video input buffer
class VideoInputBuffer : public InputBuffer<cv::Mat> {
    FrameSize frameSize;

    public:
        VideoInputBuffer();
        VideoInputBuffer(int height, int width);
        void capture();

        // TEMP - just for testing; will be deleted later
        void show();
};

#endif