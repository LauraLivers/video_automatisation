import cv2
import numpy as np
from color_grading import _add_audio
from collections import deque
import os
import random
import subprocess


def rgb_trail(video_input_path, video_output_path, red_lag=0, green_lag=5, blue_lag=10):
    """ Applies a lag to RGB Channels.
        lag unit    : fps
        trigger     : % chance
        duration    : [1, 3] seconds """
    cap = cv2.VideoCapture(video_input_path)
    if not cap.isOpened():
        raise ValueError("rgb trail: Input video can't be opened")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)  # Do not cast to int to preserve exact FPS
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    temp_video = 'temp_video.mp4'
    out = cv2.VideoWriter(temp_video, fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        raise ValueError("rgb trail: Output video can't be created")

    red_queue = deque(maxlen=max(red_lag, green_lag, blue_lag) + 1)
    green_queue = deque(maxlen=max(red_lag, green_lag, blue_lag) + 1)
    blue_queue = deque(maxlen=max(red_lag, green_lag, blue_lag) + 1)

    frame_count = 0
    prev_time = 0
    effect_active = False
    effect_end_frame = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        b, g, r = cv2.split(frame)

        red_queue.append(r)
        green_queue.append(g)
        blue_queue.append(b)

        # Handle effect activation with a random chance
        if not effect_active and random.random() < 0.01:  # 1% chance per frame
            effect_active = True
            effect_duration = random.randint(int(fps * 1), int(fps * 3))  # Duration between 1 to 3 seconds
            effect_end_frame = frame_count + effect_duration
        if effect_active and frame_count >= effect_end_frame:
            effect_active = False

        if effect_active:
            r_lagged = red_queue[-red_lag - 1] if red_lag < len(red_queue) else r
            g_lagged = green_queue[-green_lag - 1] if green_lag < len(green_queue) else g
            b_lagged = blue_queue[-blue_lag - 1] if blue_lag < len(blue_queue) else b
        else:
            r_lagged, g_lagged, b_lagged = r, g, b

        aberrated_frame = cv2.merge((b_lagged, g_lagged, r_lagged))

        # Ensure frames are written in sync with exact time progression
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # Get current time in seconds
        if current_time > prev_time:  # Only write if the time progresses
            out.write(aberrated_frame)
            prev_time = current_time

        frame_count += 1
        if frame_count % 100 == 0 or frame_count == total_frames:
            print(f"RGB Trail: Processed {frame_count} / {total_frames} frames")

    cap.release()
    out.release()

    _add_audio(video_input_path, temp_video, video_output_path)
    if os.path.exists(temp_video):
        os.remove(temp_video)


def apply_slow_motion(input_video, output_video, slow_down_factor=0.5):
    cmd = [
        'ffmpeg',
        '-i', input_video,
        '-filter:v', f"setpts={slow_down_factor}*PTS",
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '0:a:0',
        '-y',
        output_video
    ]
    subprocess.run(cmd, check=True)
    print(f"Video saved in slow motion to: {output_video}")