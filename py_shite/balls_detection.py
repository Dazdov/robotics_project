import cv2
import torch
import torchvision
from torchvision.transforms import functional as F

# Load the pre-trained model
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Define a function to process frames
def process_frame(frame, model, threshold=0.5):
    # Convert the frame to a PIL image and transform it for the model
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = F.to_pil_image(frame_rgb)
    tensor_image = F.to_tensor(pil_image).unsqueeze(0)
    
    # Perform object detection
    with torch.no_grad():
        predictions = model(tensor_image)[0]
    
    # Draw bounding boxes for detected objects
    for box, label, score in zip(predictions['boxes'], predictions['labels'], predictions['scores']):
        if score >= threshold:  # Adjust this threshold based on your needs
            x1, y1, x2, y2 = box.int().tolist()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Object: {score:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

# Open the webcam (camera ID 0 is typically the default camera)
camera_id = 0  # Change this if you have multiple cameras
cap = cv2.VideoCapture(camera_id)

# Check if the webcam is opened successfully
if not cap.isOpened():
    print("Error: Cannot access the camera.")
    exit()

print("Press 'q' to exit the live feed.")

# Process the video feed frame by frame
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read frame from camera.")
        break

    # Detect objects in the current frame
    processed_frame = process_frame(frame, model)
    
    # Display the frame with detections
    cv2.imshow("Live Ball Detection", processed_frame)
    
    # Press 'q' to exit the live video feed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
