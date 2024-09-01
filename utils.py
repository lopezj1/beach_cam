import time
import yt_dlp as ytdlp
from yt_dlp.utils import download_range_func
from config import YOUTUBE_URL

def download_video():
    # Options for yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'last_5_minutes.mp4',  # Output filename
        "download_ranges": download_range_func(None, [(60, 75)]),
    }

    # Download the video using the defined options
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([YOUTUBE_URL])
    
def get_stream_url():
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True
    }
    
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
        formats = info_dict.get('formats', [])
        for format in formats:
            print(format)
            if format.get('protocol') == 'https':
                return format.get('url')
        return None
