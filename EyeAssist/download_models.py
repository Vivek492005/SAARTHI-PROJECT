import os
import urllib.request

def download_file(url, filename):
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded {filename} successfully!")

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # YOLOv3 files
    yolo_files = {
        'yolov3.weights': 'https://pjreddie.com/media/files/yolov3.weights',
        'yolov3.cfg': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg',
        'coco.names': 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
    }
    
    for filename, url in yolo_files.items():
        if not os.path.exists(os.path.join('models', filename)):
            download_file(url, os.path.join('models', filename))
        else:
            print(f"{filename} already exists, skipping download.")
    
    print("\nAll required model files are ready!")

if __name__ == "__main__":
    main()
