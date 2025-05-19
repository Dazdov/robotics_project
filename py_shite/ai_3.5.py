import cv2
import threading
import tempfile
import time
import serial
from inference_sdk import InferenceHTTPClient

# === Constants ===
API_KEY = "TY2c0swGjZnlQrqQiHSG"
MODEL_ID = "ball_set-lyem5/3"
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
CONFIDENCE_THRESHOLD = 0.50

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
def process_and_display_frame():
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
                if label == "Soccer ball":
                    time.sleep(0.2)
                    if x < 270:
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

# === Main Application Logic ===
def main():
    initialize()

    # Start threads
    threading.Thread(target=capture_frame, daemon=True).start()
    threading.Thread(target=track_object_positions, daemon=True).start()

    # Main loop
    while True:
        if frame is not None:
            process_and_display_frame()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# === Run ===
if __name__ == "__main__":
    main()