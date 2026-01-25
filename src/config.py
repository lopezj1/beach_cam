import os
from dotenv import load_dotenv

load_dotenv()

# Video processing settings
YOUTUBE_URL = "https://www.youtube.com/watch?v=VSiQ7BLkZHw"
VIDEO_LENGTH_MINUTES = 1
VIDEO_QUALITY = "medium"
# Object detection settings
DETECTION_CLASSES = [0, 2]  # person, car
DETECTION_THRESHOLD = 0
MODEL_PATH = "./yolo_models/yolov8n.pt"

# Cloudflare R2 storage settings
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY") 
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Email notification settings
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Development overrides
DEBUG_MODE = "false"
LOG_LEVEL = "INFO"