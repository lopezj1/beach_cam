import time
import yt_dlp as ytdlp
from yt_dlp.utils import download_range_func
from config import YOUTUBE_URL

def download_video():
    
    # Options for yt-dlp
    start_time = 0
    end_time = 30
    ydl_opts = {
        'format': 'best',
        'format_sort': ['proto:https'],
        'outtmpl': 'last_30_seconds.mp4',  # Output filename
        "download_ranges": download_range_func(None, [(start_time, end_time)]),
        'verbose': True,
    }

    # Download the video using the defined options
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([YOUTUBE_URL])

    return ydl_opts.get('outtmpl')