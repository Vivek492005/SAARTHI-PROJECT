# EyeAssist - Comprehensive Visual Assistance System

EyeAssist is an integrated solution designed to assist individuals with visual impairments by combining multiple assistive technologies into a single, user-friendly application.

## Features

- **Eye Tracking**: Control the mouse cursor using eye movements
- **Object Detection**: Identify and describe objects in the environment
- **Text Recognition**: Read text from the screen or camera feed
- **Voice Feedback**: Get audio descriptions of detected objects and text
- **Accessible Interface**: Simple, easy-to-use interface with high contrast and large buttons

## Prerequisites

- Python 3.7 or higher
- Webcam
- Tesseract OCR (for text recognition)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd EyeAssist
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**:
   - Windows: Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Usage

1. **Run the application**:
   ```bash
   python main.py
   ```

2. **Calibrate the eye tracker** (first-time setup):
   - Follow the on-screen instructions to calibrate the eye tracking
   - Position yourself about 50-70cm from the camera
   - Ensure good lighting on your face

3. **Using the interface**:
   - **Gaze Control**: Move your eyes to control the cursor
   - **Click**: Stare at a point for 1.5 seconds to click
   - **Right-click**: Blink your right eye
   - **Scroll**: Look to the top or bottom of the screen

## Modules

- **Eye Tracker**: Tracks eye movements and controls the cursor
- **Object Detector**: Identifies objects in the camera feed
- **Text Recognizer**: Reads text from the screen or camera
- **Cursor Controller**: Manages mouse and keyboard input

## Customization

You can customize various settings in the `config.json` file:
- Mouse sensitivity
- Click timing
- Voice feedback settings
- Display preferences

## Troubleshooting

- **Eye tracking not working**: Ensure good lighting and that your face is clearly visible
- **Text recognition issues**: Check that Tesseract is installed and in your system PATH
- **Performance problems**: Close other applications to free up system resources

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
