from ultralytics import YOLO
import cv2
import logging
from datetime import datetime
import gc

# Global model cache to avoid reloading
_model_cache = None

def _get_model(model_path="./yolo_models/yolov8n.pt"):
    """Get or load YOLO model, caching to save memory"""
    global _model_cache
    if _model_cache is None:
        logging.info(f"Loading YOLO model from {model_path}")
        _model_cache = YOLO(model_path)
    return _model_cache

def detect_objects_and_get_alert_frame(video_path, target_classes, threshold):
    """Run YOLO detection and return alert frame if threshold exceeded"""
    
    # Load model from cache
    model = _get_model()
    logging.info(f"Starting detection on video: {video_path}")
    
    # Run detection with stride for efficiency
    results = model.predict(
        video_path,
        device='cpu',
        conf=0.5,
        classes=target_classes,
        vid_stride=40,  # Analyze every 40th frame for memory savings
        show=False,
        half=False  # Use full precision on CPU
    )
    
    max_count = 0
    best_frame = None
    best_frame_path = None
    frame_count = 0
    chunk_size = 10  # Log progress every 10 frames
    
    # Analyze results and release memory as we go
    for frame_idx, result in enumerate(results):
        try:
            boxes = result.boxes
            current_count = len(boxes)
            frame_count += 1
            
            # Log progress every chunk_size frames
            if frame_count % chunk_size == 0:
                logging.info(f"Processing chunk: Frame {frame_count} | Current detections: {current_count} objects")
            
            if current_count > max_count:
                max_count = current_count
                logging.info(f"New peak detection at frame {frame_count}: {current_count} objects")
                # Delete previous best frame to free memory
                if best_frame_path and best_frame_path != result.path:
                    try:
                        import os
                        if os.path.exists(best_frame_path):
                            os.remove(best_frame_path)
                    except Exception as e:
                        logging.warning(f"Could not remove old frame: {e}")
                
                # Save best annotated frame at lower quality
                annotated_frame = result.plot()
                best_frame_path = f"/tmp/alert_frame_{datetime.now().strftime('%H-%M-%S')}.jpg"
                # Compress JPEG to save disk space
                cv2.imwrite(best_frame_path, annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                best_frame = best_frame_path
                logging.info(f"Saved alert frame: {best_frame_path}")
                
                # Release memory from annotated frame
                del annotated_frame
            
            # Also save frame if it meets threshold and we haven't saved one yet
            elif current_count >= threshold and best_frame is None:
                best_frame = f"/tmp/alert_frame_{datetime.now().strftime('%H-%M-%S-%f')}.jpg"
                cv2.imwrite(best_frame, result.plot(), [cv2.IMWRITE_JPEG_QUALITY, 70])
                logging.info(f"Saved alert frame (threshold met): {best_frame}")
        except Exception as e:
            logging.warning(f"Error processing frame {frame_idx}: {e}")
            continue
        finally:
            # Explicitly delete result to free GPU/CPU memory
            del result
    
    # Force garbage collection
    gc.collect()
    
    logging.info(f"Detection complete: Processed {frame_count} frames, Peak detections: {max_count} objects")
    
    alert_triggered = max_count >= threshold
    
    # If no frame was saved but alert is triggered, log the issue
    if alert_triggered and best_frame is None and max_count > 0:
        logging.warning(f"Alert triggered but no peak frame saved. This may indicate detection occurred but didn't create a peak.")
    
    return {
        'object_count': max_count,
        'alert_triggered': alert_triggered,
        'alert_frame': best_frame,
        'total_frames': frame_count
    }