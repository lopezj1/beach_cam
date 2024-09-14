import cv2
import numpy as np
from config import CAR_THRESHOLD
from notifier import send_sms_alert
from utils import download_video

# Load YOLO model
net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def detect_objects(frame):
    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    class_ids = []
    confidences = []
    boxes = []
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])
            if confidence > 0.5:  # Detection threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                
                boxes.append([x, y, w, h])
                confidences.append(confidence)
                class_ids.append(class_id)
    
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    print(f'indices are {indices}')
    car_count = 0
    
    if len(indices) > 0:
        for i in indices:
            # If 'i' is a tuple, extract the first element
            i = i[0] if isinstance(i, (list, tuple)) else i
            box = boxes[i]
            x, y, w, h = box[0], box[1], box[2], box[3]

            if class_ids[i] == 2:  # Car
                car_count += 1
                label = "Car"
                color = (0, 255, 0)
            elif class_ids[i] == 0:  # Person
                label = "Person"
                color = (0, 0, 255)
            else:
                continue

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return frame, car_count

def generate_frames_from_download():
    video_file = download_video()
    print(f'video file info: {video_file}')

    # Open the video file
    cap = cv2.VideoCapture(video_file.get('default'))

    if not cap.isOpened():
        print("Error: Could not open video file.")
        return  # Exit the function gracefully

    try:
        frame_count = 0
        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame")
                break

            # Resize the frame to speed up processing
            frame = cv2.resize(frame, (640, 360))

            # Process every nth frame (e.g., every 5th frame)
            frame_count += 1
            if frame_count % 5 != 0:
                continue

            # Detect objects and count cars
            frame, car_count = detect_objects(frame)

            # Send SMS alert if car count exceeds threshold
            if car_count >= CAR_THRESHOLD:
                send_sms_alert(car_count)

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            # ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the output frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Ensure the video capture is released
        cap.release()

