import yt_dlp as ytdlp
from config import YOUTUBE_URL

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
