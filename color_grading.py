import cv2
import numpy as np
import subprocess
import os


def _teal_orange(frame, intensity=0.8):
    """ Internal Function that applies the Hollywood filter
    where shadows shift to teal and highlights to orange"""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    a = cv2.addWeighted(a, 1.0, a, 0, -10 * intensity)
    b = cv2.addWeighted(b, 1.0, b, 0, -15 * intensity)

    graded_lab = cv2.merge((l, a, b))

    return cv2.cvtColor(graded_lab, cv2.COLOR_LAB2BGR)

def _add_audio(input_video_path, processed_video_path, output_path):
    """ Internal function to retain audio """
    command = [
        'ffmpeg',
        '-y',
        '-i', processed_video_path,
        '-i', input_video_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0', # input 1: use video
        '-map', '1:a:0', # input 2: use video
        output_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def adjust_exposure(video_input, video_output, brightness=-0.05, contrast=1.05, gamma=0.95):
    """ Function to adjust brightness and contrast
        brightness : [-1, 1], 0 = original
        contrast [0, 1], 1.0 = original
        gamma [> 0], 1.0 = original, < 1.0 darken midtones, > 1.0 lighten midtones"""
    ffmpeg_command = [
        'ffmpeg',
        '-threads', '8',
        '-i', video_input,
        '-vf', f'eq=brightness={brightness}:contrast={contrast}:gamma={gamma}',
        '-preset', 'ultrafast',
        '-c:a', 'copy',
        video_output
    ]
    subprocess.run(ffmpeg_command)
    print(f'Exposure: saved video to {video_output}')



def apply_teal_orange(video_input_color, video_output_color, intensity=0.8):
    """ function to apply the teal-orange filter while retaining audio and format"""
    cap = cv2.VideoCapture(video_input_color)
    if not cap.isOpened():
        raise ValueError("T/O:Input video cannot be opened")

    # get input video properties to ensure consistency in output!
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    temp_video = 'temp_video.mp4'
    out = cv2.VideoWriter(temp_video, fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        raise ValueError(f"T/O: Output video cannot be created: {temp_video}") #debug
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = _teal_orange(frame, intensity)
        out.write(processed_frame)

        frame_count += 1
        if frame_count % 100 == 0 or frame_count == total_frames:
            print(f"T/O: Processed {frame_count} / {total_frames} frames")

    cap.release()
    out.release()
    _add_audio(video_input_color, temp_video, video_output_color)
    if os.path.exists(temp_video):
        os.remove(temp_video)



def apply_black_white(video_input_color, video_output_color):
    """ Function to turn video B/W while retaining audio and format"""
    cap = cv2.VideoCapture(video_input_color)
    if not cap.isOpened():
        raise ValueError("B/W: Input video cannot be opened")

    # get input video properties to ensure consistency in output!
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    temp_video = 'temp_video.mp4'
    out = cv2.VideoWriter(temp_video, fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        raise ValueError(f"B/W: Output video cannot be created: {temp_video}")
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frame = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
        out.write(processed_frame)

        frame_count += 1
        if frame_count % 100 == 0 or frame_count == total_frames:
            print(f"B/W: Processed {frame_count} / {total_frames} frames")

    cap.release()
    out.release()
    _add_audio(video_input_color, temp_video, video_output_color)
    if os.path.exists(temp_video):
        os.remove(temp_video)