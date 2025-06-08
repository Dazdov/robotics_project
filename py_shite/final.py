import cv2
import threading
import tempfile
import time
import serial
from inference_sdk import InferenceHTTPClient
import speech_recognition as sr
import pygame

# === Constants ===
API_KEY = "API_KEY"
MODEL_ID = "ball_set-lyem5/3"
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
CONFIDENCE_THRESHOLD = 0.60

# === Global Variables ===
frame = None
video_capture = None
arduino = None
position_lock = threading.Lock()

# === Object Tracking Data Structures ===
class_positions = {
    "Balls in general": {"x": None, "y": None, "timestamp": 0},
    "Soccer ball": {"x": None, "y": None, "timestamp": 0},
    "tennis-ball": {"x": None, "y": None, "timestamp": 0},
}
class_colors = {
    "Balls in general": (255, 0, 0),  # Blue
    "Soccer ball": (0, 255, 0),        # Green
    "tennis-ball": (0, 0, 255),        # Red
}

# === Initialize Hardware and Inference Client ===
def initialize():
    global video_capture, arduino, CLIENT
    video_capture = cv2.VideoCapture(0)
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for serial connection to stabilize
    CLIENT = InferenceHTTPClient(api_url="https://detect.roboflow.com", api_key=API_KEY)

# === Frame Capture Thread ===
def capture_frame():
    global frame
    while True:
        ret, new_frame = video_capture.read()
        if ret:
            frame = new_frame

# === Object Detection and Position Tracking Thread ===
def track_object_positions():
    global class_positions
    while True:
        if frame is not None:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_path = temp_file.name
                cv2.imwrite(temp_path, frame)

            try:
                response = CLIENT.infer(temp_path, model_id=MODEL_ID)
                if "predictions" in response:
                    current_time = time.time()
                    with position_lock:
                        for prediction in response["predictions"]:
                            if prediction["confidence"] > CONFIDENCE_THRESHOLD:
                                x, y = int(prediction["x"]), int(prediction["y"])
                                label = prediction["class"]
                                if label in class_positions:
                                    class_positions[label] = {
                                        "x": x, "y": y, "timestamp": current_time
                                    }
            except Exception as e:
                print(f"Inference error: {e}")

# === Drawing and Arduino Command Logic ===
def process_and_display_frame(chosen_ball):
    global frame
    current_time = time.time()
    with position_lock:
        for label, data in class_positions.items():
            x, y = data["x"], data["y"]
            last_seen = data["timestamp"]

            if current_time - last_seen <= 0.5 and x is not None and y is not None:
                color = class_colors[label]
                cv2.circle(frame, (x, y), 10, color, -1)
                cv2.putText(
                    frame, f"{label}", (x + 15, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )

                # Control Arduino based on "Soccer ball"
                if label == chosen_ball:
                    time.sleep(0.5)
                    if y > 370:
                        arduino.write(b'4')
                        pygame.mixer.init()
                        pygame.mixer.music.load("/home/raspberry/project3/beep.wav")
                        pygame.mixer.music.play()
                        return 404
                    elif x < 270:
                        arduino.write(b'3')  # Turn left
                    elif x > 390:
                        arduino.write(b'2')  # Turn right
                    else:
                        arduino.write(b'1')  # Move forward
            else:
                class_positions[label] = {"x": None, "y": None, "timestamp": 0}

    # Draw boundary lines
    height = frame.shape[0]
    cv2.line(frame, (270, 0), (270, height), (0, 255, 255), 2)  # Yellow left boundary
    cv2.line(frame, (390, 0), (390, height), (0, 255, 255), 2)  # Yellow right boundary

    cv2.imshow("Live Video Inference", frame)

def recognize_speech_from_mic():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use default microphone (set AirPods as default input device)
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening... Speak clearly into your AirPods.")

        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing speech...")
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text

        except sr.WaitTimeoutError:
            print("No speech detected.")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Error from Google API: {e}")

# === Main Application Logic ===
def main():
    initialize()
    chosen_ball = "tennis-ball"
    temp_voice = recognize_speech_from_mic()
    if (("tennis" in temp_voice) and (("football" in temp_voice) or ("soccer" in temp_voice))):
        print("error cant track both at the same time")
    elif (("football" in temp_voice) or ("soccer" in temp_voice)):
        chosen_ball = "Soccer ball"
    elif ("tennis" in temp_voice):
        chosen_ball = "tennis-ball"
    else:
        print("no such thing")
        return 0


    # Start threads
    threading.Thread(target=capture_frame, daemon=True).start()
    threading.Thread(target=track_object_positions, daemon=True).start()

    # Main loop
    while True:
        if frame is not None:
            a = process_and_display_frame(chosen_ball)
            if a == 404:
                pygame.mixer.init()
                try:
                    pygame.mixer.music.load("/home/raspberry/project3/beep.wav")
                    print("Sound loaded successfully")

                    # Play the sound
                    pygame.mixer.music.play()

                    # Wait while the sound is playing
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)

                except pygame.error as e:
                    print(f"Error loading or playing sound: {e}")
                return 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# === Run ===
if __name__ == "__main__":
    main()
