// should try 0x501 below instead of 0x500 if we run into error
#define _WIN32_WINNT 0x500

// headers
#include "opencv2/objdetect.hpp"`
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/video.hpp"
#include "opencv2/core/core.hpp"
#include "opencv2/features2d/features2d.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/calib3d/calib3d.hpp"
#include "opencv2/nonfree/nonfree.hpp"
#include <windows.h>
#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <vector>

// namespaces
using namespace std;
using namespace cv;

// objects
class face
{
public:
	vector<Rect> faceRects;
	int empty;
	size_t length;

	face (int a) {empty = a;}
};

// function prototypes
face detectFaceAndDisplay (Mat &frame);
int initialize (Mat &iniFrame, Mat &theTemplate, Rect &region_of_interest);
void getMousePosition ();
void mouseRightClick ();
void mouseLeftClick ();
void mouseMoveTo (int toX, int toY);

// global variables
String face_cascade_name = "haarcascade_frontalface_alt.xml";
String eyes_cascade_name = "haarcascade_eye_tree_eyeglasses.xml";
CascadeClassifier face_cascade;
CascadeClassifier eyes_cascade; 
int xPos = 0, yPos = 0, accuxPos = 0, accuyPos = 0, check = 0;
const int clickThresh = 100;
int frameRes_width = 320, frameRes_height = 240;

// main function
int main()
{
	// variable declarations
	VideoCapture capture;
	Mat frame, templ, input;
	Rect ROI;
	int captured, initialized;

	// check the video stream
	capture.open (0);
	if (!capture.isOpened ()) 
	{ 
		printf ("--(!)Error opening video capture\n"); 
		if (waitKey (0) >= 0) return -1;
	}

   	// Load the cascades
    if (!face_cascade.load (face_cascade_name)) 
	{ 
		printf ("--(!)Error loading face cascade\n"); 
		if (waitKey (0) >= 0) return -1;
	}

	// initialization - 1. detecting a face and, 2. getting a ROI
	captured = 1, initialized = 1;
	while (1)
	{
		// Read a frame
		capture.read (frame);
		if (frame.empty ())
			captured = 0;

		// resizing and mirroring the frame to reduce calculation and faster application
		if (captured)
		{			
			resize (frame,frame,Size(320,240),0,0,INTER_CUBIC);
			flip (frame, frame, 1);
			initialized = initialize (frame, templ, ROI);
		}

		frameRes_width -= (templ.cols + 20);
		frameRes_height -= (templ.rows + 15);

		if (initialized)
			break;
	}

	// live streaming and face tracking to give mouse pointer commands
	captured  = 1;
	while (1)
	{
		// Read a frame
		capture.read (frame);
		if (frame.empty ())
			captured = 0;

		// resizing and mirroring
		if (captured)
		{
			resize (frame,frame,Size(320,240),0,0,INTER_CUBIC); 
			flip (frame, frame, 1);
		}

		// croping an image out of frame Mat with size of ROI
		Mat ROIImage (frame, ROI);
		input = ROIImage;
		Mat img = input;
		
		// create the result matrix
		Mat result;
		int result_cols =  img.cols - templ.cols + 1;
		int result_rows = img.rows - templ.rows + 1;
		result.create( result_cols, result_rows, CV_32FC1 );
		
		// do the Matching and Normalize
		int match_method = CV_TM_CCOEFF_NORMED;
		matchTemplate (img, templ, result, match_method);
		normalize (result, result, 0, 1, NORM_MINMAX, -1, Mat());

		// localizing the best match with minMaxLoc
		double minVal, maxVal; 
		Point minLoc, maxLoc, matchLoc, matchLocOld;
		matchLocOld.x = 0;
		matchLocOld.y = 0;
		minMaxLoc (result, &minVal, &maxVal, &minLoc, &maxLoc, Mat());

		// for SQDIFF and SQDIFF_NORMED, the best matches are lower values. For all the other methods, the higher the better
		if( match_method  == CV_TM_SQDIFF || match_method == CV_TM_SQDIFF_NORMED )
			matchLoc = minLoc; 
		else
			matchLoc = maxLoc; 

		// draw the ractangles
		rectangle (input, matchLoc, Point( matchLoc.x + templ.cols , matchLoc.y + templ.rows ), Scalar::all(0), 2, 8, 0);
		rectangle (result, matchLoc, Point( matchLoc.x + templ.cols , matchLoc.y + templ.rows ), Scalar::all(0), 2, 8, 0);
		
		// changing the co ordinates
		if (matchLoc.x > 20)
			matchLoc.x -= 20;
		else
			matchLoc.x = 0;

		if (matchLoc.y > 15)
			matchLoc.y -= 15;
		else
			matchLoc.y = 0;


		// Show what we got
		circle (input,matchLoc, 2, Scalar (0,0,255));
		imshow ("input", input);
		imshow ("template", templ);
		
		// give mouse pointer a command to go to a position
		if ( ( abs (matchLocOld.x - matchLoc.x) > 10 || abs (matchLocOld.y - matchLoc.y) > 10 )
			&& (abs (matchLocOld.x - matchLoc.x) < 70 || abs (matchLocOld.y - matchLoc.y) < 70) );
			mouseMoveTo (matchLoc.x, matchLoc.y);
		matchLocOld = matchLoc;

		// if the pointer is still at a position do a left click
		if (check < clickThresh)
		{
			accuxPos += matchLoc.x - matchLocOld.x;
			accuyPos += matchLoc.y - matchLocOld.y;

			check++;
		}
		if (check == clickThresh)
		{
			accuxPos += matchLoc.x - matchLocOld.x;		
			accuyPos += matchLoc.y - matchLocOld.y;

			if ( accuxPos < 4 && accuyPos < 4)
				mouseLeftClick();
			
			check = 0;
		}

		// halting the program
		int sleepFlag = 0, count = 0;
		while (++count < 25)
		{
			getMousePosition ();
			cout << xPos << " " << yPos << endl << matchLoc << endl;
			if (abs (xPos - matchLoc.x) > 2 || abs (yPos - matchLoc.y) > 2)
			{
				sleepFlag = 1;
				break;
			}
		}
		while (sleepFlag)
		{
			Sleep (10);

			
			if (waitKey(20) > 0)
			{
				sleepFlag = 0;
				break;
			}
		}

		// if escaoe is pressed stop the program
		if (waitKey(20) > 0)
			break;
	}

	getchar();
    return 0;	
}

// function detectAndDisplay 
face detectFaceAndDisplay (Mat &frame)
{
	face faces(1);
    Mat frame_gray, faceROI;
   
	// some preprocessing		
    cvtColor (frame, frame_gray, COLOR_BGR2GRAY);

	// Detect faces
	face_cascade.detectMultiScale (frame_gray, faces.faceRects, 1.1, 5, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));
    
	// if faces are found show them and set the empty pointer to 0
	if (!faces.faceRects.empty())
    {        
		// set the pointer
		faces.empty = 0;
		faces.length = faces.faceRects.size() - 1;
		
		// draw ellipse on faces
		for (size_t i = 0; i <= faces.length; i++)
		{
			Point centers;
			centers.x = faces.faceRects[i].x + faces.faceRects[i].width / 2;
			centers.y = faces.faceRects[i].y + faces.faceRects[i].height / 2;
			ellipse (frame, centers, Size(faces.faceRects[i].width / 2, faces.faceRects[i].height / 2), 0, 0, 360, 
				Scalar(255, 0, 255), 4, 8, 0);
		}
		
		// Show what you got
		imshow ("Face detection", frame);
	}
	
	return faces;
}

// function initialize()
int initialize (Mat &iniFrame, Mat &theTemplate, Rect &region_of_interest)
{
	// detect face on the given image
	face detectedFace(1);
	detectedFace = detectFaceAndDisplay (iniFrame);
	if (detectedFace.empty) 
	{
		cout << "detecting face....." << endl;
		return 0;
	}

	// determine the region of interest from the prime user
	Point center;
	size_t len = detectedFace.length;
	center.x = detectedFace.faceRects[len].x + detectedFace.faceRects[len].width / 2;
	center.y = detectedFace.faceRects[len].y + detectedFace.faceRects[len].height / 2;
	
	if (!detectedFace.empty)
	{
		Mat temp (iniFrame, detectedFace.faceRects[len]);
		theTemplate = temp;

		if (detectedFace.faceRects[len].x - detectedFace.faceRects[len].width * 0.7 > 0)
			region_of_interest.x = detectedFace.faceRects[len].x - detectedFace.faceRects[len].width/2;
		else 
			region_of_interest.x = 0;

		if (detectedFace.faceRects[len].y - detectedFace.faceRects[len].height * 0.8 > 0)
			region_of_interest.y = detectedFace.faceRects[len].y - detectedFace.faceRects[len].height/2;
		else 
			region_of_interest.y = 0;

		int flag_w = 1;
		for (float i = 2.4;; i = i - 0.2)
		{
			if ((region_of_interest.x + (int)(i * detectedFace.faceRects[len].width) < 320) && flag_w )
			{
				region_of_interest.width = (int)(i * detectedFace.faceRects[len].width);
				flag_w = 0;
			}

			if (!flag_w)
			{
				frameRes_width = region_of_interest.width;
				break;
			}
		}
		int flag_h = 1;
		for (float i = 1.8;; i = i - 0.2)
		{
			if ((region_of_interest.y + (int)(i * detectedFace.faceRects[len].height) < 240) && flag_h)
			{
				region_of_interest.height = (int)(i * detectedFace.faceRects[len].height);
				flag_h = 0;
			}

			if (!flag_h)
			{
				frameRes_height = region_of_interest.height;
				break;
			}
		}

		if (flag_w || flag_h)
			cout << "cannot find suitable ROI" << endl;

	}

	return 1;
}

void getMousePosition ()
{
     // make a point and read into it, then update vars via pointers
     POINT cursorPos;
     GetCursorPos(&cursorPos);
     xPos = cursorPos.x;
     yPos = cursorPos.y; 

	 xPos = (xPos / 1365.0) * frameRes_width;
     yPos = (yPos / 767.0) * frameRes_height;
}

void mouseRightClick ()
{
     INPUT Input = {0};
     
     // right down
     Input.type = INPUT_MOUSE;
     Input.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN;
     SendInput(1,&Input,sizeof(INPUT));
     
     // right up
     ZeroMemory(&Input,sizeof(INPUT));
     Input.type = INPUT_MOUSE;
     Input.mi.dwFlags = MOUSEEVENTF_RIGHTUP;
     SendInput(1,&Input,sizeof(INPUT));
}

void mouseLeftClick ()
{
     INPUT Input = {0};
     
     // left down
     Input.type = INPUT_MOUSE;
     Input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
     SendInput(1,&Input,sizeof(INPUT));
     
     // left up
     ::ZeroMemory(&Input,sizeof(INPUT));
     Input.type = INPUT_MOUSE;
     Input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
     SendInput(1,&Input,sizeof(INPUT));
}

void mouseMoveTo (int toX, int toY)
{
	 // modify for the 65535 (as float) way we talk to the screen...
     double dx = toX*(65535.0f / frameRes_width);
     double dy = toY*(65535.0f / frameRes_height);
     
     // movement stuff
     INPUT Input = {0};
     Input.type = INPUT_MOUSE;
     Input.mi.dwFlags = MOUSEEVENTF_MOVE|MOUSEEVENTF_ABSOLUTE;
     //Input.mi.dwFlags = MOUSEEVENTF_MOVE;
     Input.mi.dx = LONG(dx);
     Input.mi.dy = LONG(dy);
     SendInput(1,&Input,sizeof(INPUT));
}