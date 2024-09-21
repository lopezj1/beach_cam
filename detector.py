import os
import time
from config import CAR_THRESHOLD

# Path to the directory containing frames
FRAMES_DIR = './data/annotated'

def generate_frames(fps=10):
    frame_files = sorted(os.listdir(FRAMES_DIR))
    frame_delay = 1 / fps  # Calculate delay to match the frame rate
    
    while True:  # Infinite loop to replay the video
        for frame_file in frame_files:
            frame_path = os.path.join(FRAMES_DIR, frame_file)

            if frame_file.lower().endswith('.jpg'):
                with open(frame_path, 'rb') as f:
                    frame = f.read()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                # Introduce delay to match the original frame rate
                time.sleep(frame_delay)

        # Optionally, add a small delay before restarting
        time.sleep(1)  # 1 second before video replay
