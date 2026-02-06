#ifndef CC_CV_FACE_DETECTOR
#define CC_CV_FACE_DETECTOR

#include "Detector.h"

cv::Point CVTemplateFaceDetector::detect(int argc, ...){
	cv::Point matchLocation;

	// assert argument number
    if(argc != 2){
		printf("[ERROR][Detector:cvfacedetect] detect - there must be 2 arguments\n");
		return matchLocation;
	}

	// get frame and face tempate from argument
	va_list ptr;
	va_start(ptr, argc);
	cv::Mat frame = va_arg(ptr, cv::Mat);
	cv::Mat faceTemplate = va_arg(ptr, cv::Mat);
	va_end(ptr);

	// create the result matrix which contains matching probability
	cv::Mat result;
	result.create(frame.rows-faceTemplate.rows+1, frame.cols-faceTemplate.cols+1, CV_32FC1);
	
	// do template matching and then normalize
	cv::matchTemplate(frame, faceTemplate, result, matchMethod);
	cv::normalize(result, result, 0, 1, cv::NORM_MINMAX, -1, cv::Mat());

	// localizing the best match with minMaxLoc
	double minValue, maxValue; 
	cv::Point minLocation, maxLocation;
	cv::minMaxLoc(result, &minValue, &maxValue, &minLocation, &maxLocation, cv::Mat());

	// for SQDIFF and SQDIFF_NORMED, the best matches are lower values. For all the other methods, the higher the better
	if( matchMethod  == cv::TM_SQDIFF || matchMethod == cv::TM_SQDIFF_NORMED )
		matchLocation = minLocation; 
	else
		matchLocation = maxLocation; 

	return matchLocation;
}

// cv::Rect CVCascadeFaceDetector::detect(cv::Mat frame){
cv::Rect CVCascadeFaceDetector::detect(int argc, ...){
	std::vector<cv::Rect> faces;
	cv::Rect face;

	// assert argument number
	if(argc != 1){
		printf("[ERROR][Detector:cvfacedetect] detect - there must be 1 argument\n");
		return face;
	}

	// get frame from argument
	va_list ptr;
	va_start(ptr, argc);
	cv::Mat frame = va_arg(ptr, cv::Mat);;
	va_end(ptr);
	
	// load the face cascades
    if (!faceCascade.load(faceCascadeName)) 
	{ 
		printf("[ERROR][Detector:cvfacedetect] detect - error loading face cascade\n"); 
		return face;
	}
	
	// converting to gray-scale image		
	cv::Mat frame_gray;
    cv::cvtColor(frame, frame_gray, cv::COLOR_BGR2GRAY);

	// detect faces
	faceCascade.detectMultiScale(frame_gray, faces, 1.1, 5, 0 | cv::CASCADE_SCALE_IMAGE, cv::Size(30, 30));
    
	// if faces are found show them and set the empty pointer to 0
	if (faces.empty()){
		printf("[WARNING][Detector:cvfacedetect] detect - no face detected\n");
		return face;
	}

	return faces.back();
}

#endif