import cv2
import pytesseract
from PIL import Image
import numpy as np

class TextRecognizer:
    def __init__(self):
        # Set Tesseract path if not in system PATH
        # pytesseract.pytesseract.tesseract_cmd = r'<path_to_tesseract>'
        pass
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.dilate(thresh, kernel, iterations=1)
        
        return processed
    
    def detect_text_regions(self, image):
        """Detect regions in the image that contain text."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by area and aspect ratio
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter out small regions and very large ones
            if 100 < area < (image.shape[0] * image.shape[1]) * 0.9:
                aspect_ratio = w / float(h)
                # Filter by aspect ratio (typical for text)
                if 0.1 < aspect_ratio < 10.0:
                    text_regions.append((x, y, w, h))
        
        return text_regions
    
    def recognize_text(self, image, preprocess=True):
        """Recognize text in the given image."""
        if preprocess:
            image = self.preprocess_image(image)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image)
        
        # Use Tesseract to do OCR on the image
        text = pytesseract.image_to_string(pil_image)
        
        return text.strip()
    
    def recognize_text_in_regions(self, image, regions):
        """Recognize text in specific regions of the image."""
        results = []
        
        for i, (x, y, w, h) in enumerate(regions):
            # Extract the region of interest
            roi = image[y:y+h, x:x+w]
            
            # Preprocess and recognize text
            processed_roi = self.preprocess_image(roi)
            text = self.recognize_text(processed_roi, preprocess=False)
            
            if text:
                results.append({
                    'region': (x, y, w, h),
                    'text': text
                })
        
        return results
