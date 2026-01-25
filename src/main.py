#!/usr/bin/env python3
import logging
import os
import gc
import sys
from datetime import datetime

from .video_processor import download_and_process_stream
from .detector import detect_objects_and_get_alert_frame
from .utils import upload_to_r2, send_alert_email
from .config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def cleanup_file(filepath):
    """Safely remove a file"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"Cleaned up: {filepath}")
    except Exception as e:
        logging.warning(f"Could not clean up {filepath}: {e}")

def main():
    """Main processing pipeline optimized for memory efficiency"""
    video_path = None
    alert_frame_path = None
    
    try:
        logging.info("Starting beach cam processing cycle")
        
        # Download video
        video_path = download_and_process_stream(
            YOUTUBE_URL, 
            VIDEO_LENGTH_MINUTES
        )
        
        if not os.path.exists(video_path):
            raise Exception("Video download failed")
        
        logging.info(f"Video downloaded: {video_path}")
        
        # Run detection
        detection_results = detect_objects_and_get_alert_frame(
            video_path, 
            DETECTION_CLASSES, 
            DETECTION_THRESHOLD
        )
        
        alert_frame_path = detection_results['alert_frame']
        logging.info(f"Detection complete: {detection_results['object_count']} objects detected")
        logging.info(f"Alert threshold: {DETECTION_THRESHOLD} | Triggered: {detection_results['alert_triggered']}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        video_filename = f"beach-cam-{timestamp}.mp4"
        
        # Upload to R2
        upload_url = upload_to_r2(video_path, video_filename)
        
        if not upload_url:
            raise Exception("R2 upload failed")
        
        logging.info(f"Upload completed: {video_filename}")
        
        # Clean up video file immediately after upload to free disk space
        cleanup_file(video_path)
        video_path = None
        
        # Force garbage collection
        gc.collect()
        
        # Send alert if threshold exceeded
        if detection_results['alert_triggered']:
            logging.info(f"Threshold met. Sending alert email...")
            logging.info(f"Alert frame path: {alert_frame_path}")
            logging.info(f"Email config - Host: {os.getenv('EMAIL_SMTP_HOST')}, User: {os.getenv('EMAIL_USERNAME')}, Recipient: {os.getenv('RECIPIENT_EMAIL')}")
            send_alert_email(
                detection_results['object_count'],
                alert_frame_path,
                upload_url,
                timestamp
            )
            logging.info(f"Alert sent: {detection_results['object_count']} objects detected")
        else:
            logging.info(f"Alert not triggered: {detection_results['object_count']} objects < {DETECTION_THRESHOLD} threshold")
        
        # Final cleanup
        cleanup_file(alert_frame_path)
        alert_frame_path = None
        
        logging.info(f"Processing completed: {video_filename}")
        
    except Exception as e:
        logging.error(f"Processing failed: {str(e)}")
        # Cleanup on error
        cleanup_file(video_path)
        cleanup_file(alert_frame_path)
        raise
    finally:
        # Final garbage collection
        gc.collect()

if __name__ == "__main__":
    main()