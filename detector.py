import cv2
import time
import numpy as np
from config import CAR_THRESHOLD
from notifier import send_sms_alert
from utils import download_stream

# Load YOLO model
net = cv2.dnn.readNet("./yolo_models/yolov4.weights", "./yolo_models/yolov4.cfg")
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
    object_id = 0  # Counter for unique IDs
    
    if len(indices) > 0:
        for i in indices:
            # If 'i' is a tuple, extract the first element
            i = i[0] if isinstance(i, (list, tuple)) else i
            box = boxes[i]
            x, y, w, h = box[0], box[1], box[2], box[3]

            # Set label and color based on class ID
            if class_ids[i] == 2:  # Car
                car_count += 1
                label = f"Car ID:{object_id} Conf:{confidences[i]:.2f}"
                color = (0, 255, 0)
            elif class_ids[i] == 0:  # Person
                label = f"Person ID:{object_id} Conf:{confidences[i]:.2f}"
                color = (0, 0, 255)
            elif class_ids[i] == 6:  # Truck
                label = f"Truck ID:{object_id} Conf:{confidences[i]:.2f}"
                color = (255, 0, 0)
            elif class_ids[i] == 7:  # Boat
                label = f"Boat ID:{object_id} Conf:{confidences[i]:.2f}"
                color = (0, 255, 255)
            elif class_ids[i] == 13:  # Bird
                label = f"Bird ID:{object_id} Conf:{confidences[i]:.2f}"
                color = (255, 255, 0)
            else:
                object_id += 1
                continue

            # Draw bounding box and label
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            object_id += 1  # Increment the unique ID counter
    else:
        # No objects found, display 'No Object Found'
        cv2.putText(frame, 'No Object Found', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return frame, car_count

def generate_frames_from_download():
    video_file = download_stream()
    print(f'video file info: {video_file}')

    # Open the video file
    cap = cv2.VideoCapture(video_file)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    loop_reset_flag = False  # Track loop reset

    try:
        while True:
            success, frame = cap.read()

            # If we fail to grab a frame, loop the video
            if not success:
                print("Reached end of video, looping back to start.")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the first frame
                loop_reset_flag = True  # Set loop reset flag
                continue

            frame = cv2.resize(frame, (640, 360))  # Resize frame to speed up processing

            # Normal frame processing
            frame, car_count = detect_objects(frame)

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            frame = buffer.tobytes()

            # Add loop reset header to the first frame after looping
            if loop_reset_flag:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'X-Loop-Reset: true\r\n\r\n' + frame + b'\r\n')
                loop_reset_flag = False  # Reset the flag after sending
                # Wait briefly to ensure the header is properly processed
                time.sleep(0.1)
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

