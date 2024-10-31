#!/bin/bash

python3 -c "from utils import download_stream; download_stream()"

sleep 30

python3 -c "from utils import detect_objects; detect_objects()"

sleep 30

python3 -c "from utils import save_video_from_frames; save_video_from_frames()"
