import cv2
import pytesseract
import numpy as np

class TextRecognizer:
    def __init__(self):
        # Configure Tesseract parameters
        self.config = '--oem 3 --psm 6'  # PSM 6: Assume a single uniform block of text
        
    def preprocess_image(self, image):
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        processed = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.dilate(processed, kernel, iterations=1)
        
        return processed
    
    def detect_text_regions(self, image):
        """Detect regions in the image that likely contain text."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 
            11, 2
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
            min_area = 100  # Minimum area to be considered as text
            max_area_ratio = 0.9  # Maximum area ratio to frame size
            
            if (min_area < area < (image.shape[0] * image.shape[1]) * max_area_ratio):
                aspect_ratio = w / float(h)
                # Filter by aspect ratio (typical for text)
                if 0.1 < aspect_ratio < 10.0:
                    # Add some padding
                    padding = 5
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(image.shape[1] - x, w + 2 * padding)
                    h = min(image.shape[0] - y, h + 2 * padding)
                    text_regions.append((x, y, w, h))
        
        return text_regions
    
    def recognize_text(self, image, preprocess=True):
        """Recognize text in the given image."""
        if preprocess:
            image = self.preprocess_image(image)
        
        # Use Tesseract to do OCR on the image
        text = pytesseract.image_to_string(image, config=self.config)
        
        return text.strip()
    
    def recognize_text_in_regions(self, image, regions):
        """Recognize text in specific regions of the image."""
        results = []
        
        for i, (x, y, w, h) in enumerate(regions):
            # Extract the region of interest
            roi = image[y:y+h, x:x+w]
            
            # Skip empty regions
            if roi.size == 0:
                continue
                
            try:
                # Preprocess and recognize text
                processed_roi = self.preprocess_image(roi)
                text = self.recognize_text(processed_roi, preprocess=False)
                
                if text.strip():
                    results.append({
                        'region': (x, y, w, h),
                        'text': text.strip()
                    })
            except Exception as e:
                print(f"Error processing region {i}: {str(e)}")
                continue
        
        return results
    
    def draw_text_regions(self, frame, regions, color=(0, 255, 0), thickness=2):
        """Draw rectangles around detected text regions."""
        for (x, y, w, h) in regions:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        return frame
