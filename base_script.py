import cv2
import yt_dlp as ytdlp
import os
import time

# URL of the YouTube video
youtube_url = "https://www.youtube.com/watch?v=RbqP5W5P3yg"  # Replace with your YouTube video URL

def download_video(youtube_url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'temp_video.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }
    
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
        # info_dict = ydl.extract_info(youtube_url, download=False)
        # print(info_dict['formats'][0])
        # video_file = 'temp_video.' + info_dict['formats'][0]['ext']
        video_file = 'temp_video.' + 'mkv'
        return video_file

# Download the video
# video_file = 'temp_video.mkv'
# video_file = 'Live Beach Cam： Seaside Heights [RbqP5W5P3yg].mkv'
video_file = download_video(youtube_url)

# time.sleep(10)
# print(video_file)

# Open the video file
cap = cv2.VideoCapture(video_file)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Display the frame in an OpenCV window
    cv2.imshow("YouTube Video", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and delete the video file
cap.release()
cv2.destroyAllWindows()
os.remove(video_file)
