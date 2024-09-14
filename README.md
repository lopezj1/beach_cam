# NJ Beach Cam Object Detection Notifier

This project downloads a specific time range from a live stream of a NJ beach, detects objects (cars and people) in using OpenCV, and sends Twilio notifications when a threshold of detected cars is met.

## Features

- Download specific portions of YouTube videos.
- Detect cars and people in a video stream.
- Send Twilio notifications when a car detection threshold is reached.
- Output video stream to a web browser via Flask.

## Setup

### Prerequisites

- Python 3.x
- yt-dlp for downloading videos.
- OpenCV for video processing.
- Twilio for notifications.

### Installation

1. Clone the repository and navigate to the project directory.

    ```
    git clone https://github.com/yourusername/yt-dlp-object-detection.git
    cd yt-dlp-object-detection
    ```

2. Install dependencies

    ```
    pip install -r requirements.txt
    ```

3. Set up Twilio by adding your account details to environment variables.

    ```
    export TWILIO_ACCOUNT_SID='your_account_sid'
    export TWILIO_AUTH_TOKEN='your_auth_token'
    export TWILIO_PHONE_NUMBER='your_twilio_number'
    export YOUR_PHONE_NUMBER='your_phone_number'
    ```

4. Add the YouTube video URL in the configuration file.

    ```
    YOUTUBE_URL = "https://www.youtube.com/watch?v=your_video_id"
    ```

## Run Project

The Flask app processes the video stream, detects objects (cars and people), and sends notifications when a threshold of detected cars is reached.

1. Run the Flask app to initiate the video stream and object detection.

    ```
    python app.py
    ```

2. Visit http://localhost:5000 to view real-time detection results.
