import yt_dlp as ytdlp
import os
import logging
import shutil
from datetime import datetime

def download_and_process_stream(youtube_url, duration_minutes=5):
    """Download video segment and convert to MP4"""
    
    # Generate unique filename in /tmp directory
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_template = f"/tmp/temp_video_{timestamp}.%(ext)s"
    
    # Check for Node.js availability for YouTube JS runtime
    node_path = shutil.which('node')
    
    ydl_opts = {
        'format': 'best[height<=480]/best',  # Lower resolution for memory efficiency
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
        'socket_timeout': 30,
        'http_chunk_size': 10485760,  # 10MB chunks
    }
    
    # Add JS runtime if Node.js is available
    if node_path:
        ydl_opts['js_runtimes'] = {'node': {}}
        logging.info(f"Using Node.js runtime for JavaScript: {node_path}")
    else:
        logging.warning("Node.js not found. YouTube extraction may fail for some formats.")
    
    try:
        with ytdlp.YoutubeDL(ydl_opts) as ydl:
            logging.info(f"Starting download from {youtube_url}")
            ydl.download([youtube_url])
    except Exception as e:
        logging.error(f"Video download failed: {e}")
        raise
    
    # Return path to downloaded video
    video_path = output_template.replace('%(ext)s', 'mp4')
    logging.info(f"Video download complete: {video_path}")
    return video_path