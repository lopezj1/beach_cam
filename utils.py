import os
import requests
import ffmpeg
import yt_dlp as ytdlp
from yt_dlp.utils import download_range_func
from config import YOUTUBE_URL, DATA_DIR

def download_video():
    '''
    Downloads non-live stream youtube video into .mp4 format
    '''
    # Options for yt-dlp
    start_time = 0
    end_time = 30
    ydl_opts = {
        'format': 'best',
        'format_sort': ['proto:https'],
        'outtmpl': 'output.mp4',  # Output filename
        "download_ranges": download_range_func(None, [(start_time, end_time)]),
        'verbose': True,
    }

    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([YOUTUBE_URL])

    return ydl_opts.get('outtmpl')

def download_m3u8_playlist():
    '''
    Downloads the m3u8 playlist file
    '''
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Options for yt-dlp
    ydl_opts = {
        'quiet': True,  # Suppresses download logs
        'skip_download': True  # We only want to extract info, not download
    }
    
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
        
    playlist_url = info_dict.get('url')
    response = requests.get(playlist_url)
    file_path = os.path.join(DATA_DIR, 'playlist.m3u8')
    
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print('Playlist file downloaded successfully')
        return file_path
    else:
        print('Failed to download playlist file')
        return None

def get_last_segments(m3u8_content, num_segments=5):
    '''Returns list of segment urls'''
    lines = m3u8_content.strip().splitlines()
    segment_urls = [line for line in lines if not line.startswith("#")]
    
    return segment_urls[-num_segments:]

def download_segments(segment_urls):
    '''
    Download the .ts segment files from the m3u8 playlist 
    into ./data/segments directory
    '''
    segments_dir = os.path.join(DATA_DIR, 'segments')
    if not os.path.exists(segments_dir):
        os.makedirs(segments_dir)

    segment_files = []
    for i, url in enumerate(segment_urls):
        local_filename = os.path.join(segments_dir, f'segment_{i}.ts')
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_filename, 'wb') as file:
                [file.write(chunk) for chunk in response.iter_content(chunk_size=1024) if chunk]
                        
            segment_files.append(local_filename)
            print(f'Segment_{i} downloaded successfully')
        else:
            print(f"Failed to download segment: {url}")

    return segment_files

def combine_segments_to_avi(segment_files, output_file='output.avi'):
    '''
    Concatenates all *.ts files and outputs as .avi file
    '''    
    segments_to_concat = []
    [segments_to_concat.append(ffmpeg.input(segment_file)) for segment_file in segment_files]
    
    output_file_path = os.path.join(DATA_DIR, output_file)
    ffmpeg.concat(*segments_to_concat).output(output_file_path,f='avi').run(overwrite_output=True)
    
    print(f'Combined video saved to {output_file_path}')

    return output_file_path

def download_stream() -> str:
    '''
    Main function to download live youtube stream into .avi file
    Returns output file path as string
    '''

    m3u8_file_path = download_m3u8_playlist()
    
    if not m3u8_file_path:
        print('Exiting due to failed playlist download.')
        return

    with open(m3u8_file_path, 'r') as file:
        m3u8_content = file.read()
    
    segment_urls = get_last_segments(m3u8_content)
    segment_files = download_segments(segment_urls)
    output_file_path = combine_segments_to_avi(segment_files)

    return output_file_path

def cleanup_tmp_files():
    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)

        if filename.endswith(".ts") or filename.endswith(".m3u8"):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")