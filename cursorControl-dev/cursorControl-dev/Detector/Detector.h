#ifndef CC_FACE_DETECTOR
#define CC_FACE_DETECTOR

#include "opencv2\core.hpp"
#include "opencv2\core\core.hpp"
#include "opencv2\core\base.hpp"
#include "opencv2\core\mat.hpp"
#include "opencv2\core\types.hpp"
#include <opencv2\core\utility.hpp>
#include "opencv2\imgproc.hpp"
#include "opencv2\objdetect.hpp"
#include "opencv2\highgui.hpp"

#include <cstdarg>
#include <vector>

// base class for face detector
template <typename DetectedOutput>
class Detector{
    int type;
    public:
        virtual DetectedOutput detect(int argc, ...) = 0;
};

// class for face detector using opencv tempalte matching
class CVTemplateFaceDetector : public Detector<cv::Point>{
    int matchMethod = cv::TM_CCOEFF_NORMED;
    public:
        cv::Point detect(int argc, ...);
};

// class for face detector using opencv haar cascade classifier
class CVCascadeFaceDetector : public Detector<cv::Rect>{
    cv::String faceCascadeName = cv::samples::findFile("haarcascades\\haarcascade_frontalface_alt.xml");
    cv::CascadeClassifier faceCascade;
    public:
        cv::Rect detect(int argc, ...);
};

#endif