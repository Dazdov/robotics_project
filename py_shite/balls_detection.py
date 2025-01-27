import cv2
import threading
import tempfile
import time
from inference_sdk import InferenceHTTPClient

# Initialize the inference client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="YOUR_API_KEY" 
)

video_capture = cv2.VideoCapture(0)
class_positions = {
    "Balls in general": {"x": None, "y": None, "timestamp": 0},
    "Soccer ball": {"x": None, "y": None, "timestamp": 0},
    "tennis-ball": {"x": None, "y": None, "timestamp": 0},
}
class_colors = {
    "Balls in general": (255, 0, 0),  # Blue
    "Soccer ball": (0, 255, 0),       # Green
    "tennis-ball": (0, 0, 255),       # Red
}
frame = None
position_lock = threading.Lock()

def capture_frame():
    global frame
    while True:
        ret, new_frame = video_capture.read()
        if ret:
            frame = new_frame
#track
def track_object_positions():
    global class_positions
    while True:
        if frame is not None:
            # tempfile
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_path = temp_file.name
                cv2.imwrite(temp_path, frame)

            try:
                response = CLIENT.infer(temp_path, model_id="ball_set-lyem5/3")

                if "predictions" in response:
                    current_time = time.time()
                    with position_lock:
                        for prediction in response["predictions"]:
                            confidence = prediction["confidence"]
                            
                            if confidence > 0.65:
                                x, y = int(prediction["x"]), int(prediction["y"])
                                label = prediction["class"]

                                if label in class_positions:

                                    class_positions[label]["x"] = x
                                    class_positions[label]["y"] = y
                                    class_positions[label]["timestamp"] = current_time
            except Exception as e:
                print(f"Inference error: {e}")

capture_thread = threading.Thread(target=capture_frame, daemon=True)
tracking_thread = threading.Thread(target=track_object_positions, daemon=True)

capture_thread.start()
tracking_thread.start()

while True:
    if frame is not None:
        current_time = time.time()

        with position_lock:
            for label, data in class_positions.items():
                x, y = data["x"], data["y"]
                last_seen = data["timestamp"]

    
                if current_time - last_seen <= 5 and x is not None and y is not None:

                    color = class_colors[label]
                    cv2.circle(frame, (x, y), 10, color, -1) 
                    cv2.putText(
                        frame,
                        f"{label}",
                        (x + 15, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2,
                    )
                else:
   
                    class_positions[label] = {"x": None, "y": None, "timestamp": 0}

        cv2.imshow("Live Video Inference", frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
