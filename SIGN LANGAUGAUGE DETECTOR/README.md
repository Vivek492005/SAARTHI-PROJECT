# AI-Powered Hand Gesture Detection with Voice Assistant

An assistive technology that enables mute or speech-impaired individuals to communicate using hand gestures and voice feedback.

## 🚀 Features

- Real-time hand gesture recognition using MediaPipe
- 15+ predefined gestures with voice feedback
- Text-to-speech functionality for gesture translation
- Simple and intuitive interface
- Works with standard webcams

## ✋ Supported Gestures

1. 👍 Thumbs Up - "Yes"
2. 👎 Thumbs Down - "No"
3. 🖐️ Open Hand - "Hello"
4. ✊ Fist - "Stop"
5. ✌️ Peace Sign - "Peace"
6. 👌 OK Sign - "Okay"
7. 🤙 Call Me - "Call me"
8. 🤘 Rock On - "Rock on"
9. 🤟 I Love You - "I love you"
10. ☝️ Point Up - "Look up"
11. 👇 Point Down - "Look down"
12. 👈 Point Left - "Look left"
13. 👉 Point Right - "Look right"
14. 🤙 Shaka - "Hang loose"
15. 🕷️ Spiderman - "With great power comes great responsibility"

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sign-language-detector
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. Run the gesture assistant:
   ```bash
   python gesture_assistant.py
   ```

2. Position your hand in front of the webcam and try different gestures.

3. The system will detect your gestures and provide voice feedback.

4. Press 'q' to quit the application.

## 🤖 How It Works

The system uses MediaPipe for hand tracking and gesture recognition. It captures video from your webcam, processes each frame to detect hand landmarks, and matches the detected hand pose to a predefined set of gestures. When a gesture is recognized, the corresponding text is converted to speech using pyttsx3.

## 🛠️ Customization

You can easily customize the gestures and their corresponding voice responses by modifying the `gesture_actions` dictionary in the `gesture_assistant.py` file.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MediaPipe for the hand tracking model
- OpenCV for computer vision processing
- pyttsx3 for text-to-speech functionality
