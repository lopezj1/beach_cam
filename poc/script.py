import os
import cv2
import numpy as np
from twilio.rest import Client

# Twilio setup
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
recipient_phone_number = os.getenv('RECIPIENT_PHONE_NUMBER')

client = Client(account_sid, auth_token)

# Load YOLO model
net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Define the classes for object detection
classes = ["person", "car", "bicycle", "motorbike", "bus", "truck"]

# Load the live stream
stream_url = "https://www.youtube.com/embed/RbqP5W5P3yg?si=Y1CfDdVkqfscskFq&amp;controls=0"
cap = cv2.VideoCapture(stream_url)

# Set the car detection threshold
car_threshold = 5
notification_sent = False

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    height, width, channels = frame.shape

    # Prepare the frame for YOLO
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Analyze the detection results
    class_ids = []
    confidences = []
    boxes = []
    car_count = 0

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and classes[class_id] == "car":
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
                car_count += 1

    # Non-max suppression to remove overlaps
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw bounding boxes on the detected objects
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = (255, 0, 0)  # Blue color for cars
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Check if the car count exceeds the threshold and send notification
    if car_count >= car_threshold and not notification_sent:
        message = client.messages.create(
            body=f"Alert: Car count threshold exceeded! {car_count} cars detected.",
            from_=twilio_phone_number,
            to=recipient_phone_number
        )
        print(f"Notification sent: {message.sid}")
        notification_sent = True

    # Display the resulting frame
    cv2.imshow("Live Stream", frame)

    # Reset notification flag every few seconds (or per your logic)
    if cv2.waitKey(3000) & 0xFF == ord('r'):  # 'r' to reset notification
        notification_sent = False

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
cv2.destroyAllWindows()
