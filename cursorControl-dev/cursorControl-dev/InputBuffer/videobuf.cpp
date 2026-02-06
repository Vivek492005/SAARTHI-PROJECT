#ifndef CC_VIDEO_INPUT_BUFFER
#define CC_VIDEO_INPUT_BUFFER

#include "InputBuffer.h"

template <typename Input> Input InputBuffer<Input>::get(){
    Input input;
    if(!inputBuffer.empty()){
        input = inputBuffer.front();
        inputBuffer.pop();
    }
    return input;
}

VideoInputBuffer::VideoInputBuffer(){
    frameSize.height = 320;
    frameSize.width = 240;
}

VideoInputBuffer::VideoInputBuffer(int height, int width){
    frameSize.height = height;
    frameSize.width = width;
}

void VideoInputBuffer::capture(){
    cv::VideoCapture capture;
    cv::Mat frame;

    // open webcam to capture a frame
    capture.open (0);
    if (!capture.isOpened ()) { 
        printf ("[ERROR][InputBuffer:videobuf] VideoInputBUffer - could not open camera\n"); 
        if (cv::waitKey (0) >= 0) return;
    }
    
    // capture a frame
    capture.read (frame);
    capture.release();
    if (frame.empty ()) {
        printf ("[ERROR][InputBuffer:videobuf] VideoInputBUffer - failed tp capture frame\n");
        return; 
    }

    // resizing and mirroring the frame to reduce calculation and faster application
    cv::resize (frame, frame, cv::Size(frameSize.height, frameSize.width), 0, 0, cv::INTER_CUBIC);
    cv::flip (frame, frame, 1);

    // insert the captured frame into buffer
    put(frame);
}

// TEMP - just for testing; will be deleted later
void VideoInputBuffer::show(){
    cv::Mat currentFrame(cv::Size(frameSize.height, frameSize.width), -1);
    currentFrame = get();
    cv::imshow("test get", currentFrame);
    cv::waitKey();
}

#endif