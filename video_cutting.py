import os
import librosa
import subprocess
from scipy.signal import correlate
import numpy as np
import random


def extract_beats_from_song(song_file):
    """ Extract beats from original and return sequence for reference use """
    # y: load audio as waveform (1-D numpy float array)
    # sr: store Sampling Rate (default mono resampled at 22050Hz)
    y, sr = librosa.load(song_file, sr=None)
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # convert frame numbers (beat_frames) into timings
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    # names for later use
    beat_sequence = [{"id": f"beat{i+1}", "time": beat_time} for i, beat_time in enumerate(beat_times)]
    return beat_sequence

def _extract_audio_from_video(video_file, output_audio):
    """ Internal function to extract audio from video files to
    compare with beat_sequence """
    cmd = [
        'ffmpeg',
        '-i', video_file, # i: input
        '-q:a', '0', #q:a set audio quality (0= best, 0=worst)
        '-map', 'a', #map: select stream from input file (a=audio, v=video, s=subtitle, t=all data)
        output_audio, #output filename
        '-y', #enforce overwriting file
        '-loglevel', 'error' # supress default message
    ]
    subprocess.run(cmd, check=True)
    return output_audio


def _align_song_to_video(song_file, video_audio):
    """ Internal function to align the beats from the original song
    with the video audio using cross-correlation. """
    song, sr_song = librosa.load(song_file, sr=None)
    video, sr_video = librosa.load(video_audio, sr=None)
    # ensure consistent sampling rate
    if sr_song != sr_video:
        video = librosa.resample(video, orig_sr=sr_video, target_sr=sr_song)
    # correlate original-audio with video-audio to find similarity
    correlation = correlate(video, song, mode='full')
    # contains all possible shifts from correlation => find maximum
    lag = np.argmax(correlation) - len(song)
    # divide lag by sampling rate to get offset in seconds
    offset_time = lag / sr_song
    print(f"Offset between song and video: {offset_time:.2f} seconds") # debug
    return offset_time

def cut_videos_by_song_beats(video_folder, beat_sequence, song_file, output_dir):
    """ Cut video based on beat sequence from the original song file."""
    os.makedirs(output_dir, exist_ok=True)
    video_files = [
        os.path.join(video_folder, f)
        for f in os.listdir(video_folder)
        if f.endswith(('.mp4', '.MP4','.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV' ))
    ]
    print("Detected video files:", video_files) # debug

    if not video_files:
        print("Error: No video files found in the folder.")
        return
    clips_by_beat = {beat['id']: [] for beat in beat_sequence}
    # iterate over videos
    for video_index, video_file in enumerate(video_files, start=1):
        # set up
        audio_output = os.path.join(output_dir, f"video{video_index}.wav")
        _extract_audio_from_video(video_file, audio_output)
        offset = _align_song_to_video(song_file, audio_output)
        # iterate over beat_sequence from original-audio
        for i, beat in enumerate(beat_sequence):
            # ensure start aligns with calculated lag between original-audio and video
            beat_start = beat['time'] + offset
            if i + 1 < len(beat_sequence):
                beat_end = beat_sequence[i + 1]['time'] + offset
            else:
                # Default value in seconds for the last beat
                beat_end = beat_start + 9.5
            # get rid of invalid beats
            if beat_start < 0:
                continue
            output_file = os.path.join(
                output_dir, f"{beat['id']}_video{video_index}.mp4"
            )
            cmd = [
                'ffmpeg',
                '-ss', f"{beat_start:.2f}", # start time
                '-i', video_file,
                '-to', f"{beat_end - beat_start:.2f}", #length
                '-c:v', 'libx264', # video codec for H.254 format
                '-preset', 'ultrafast', # fast processing, might bloat file-size
                '-c:a', 'aac', # audio-codec used for compression
                '-loglevel', 'quiet',
                output_file
            ]
            subprocess.run(cmd, check=True)
            clips_by_beat[beat['id']].append(output_file)

    return clips_by_beat

def concatenate_clips_randomly(clips_by_beat, beat_sequence, output_file, song_file):
    """ Concatenate random video clips according to beat_sequence"""
    concat_file = os.path.join(os.path.dirname(output_file), "concat_list.txt")
    with open(concat_file, 'w') as f:
        for beat in beat_sequence:
            if clips_by_beat[beat['id']]:
                # for every beat in sequence chose a random take
                chosen_clip = random.choice(clips_by_beat[beat['id']])
                clip_path = os.path.abspath(chosen_clip)
                f.write(f"file '{clip_path}'\n")
    cmd = [
        'ffmpeg',
        '-f', 'concat', #specify format of input/output
        '-safe', '0',
        '-i', concat_file,
        '-i', song_file,
        '-map', '0:v:0',  # input 1: video
        '-map', '1:a:0',  # input 2: audio
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-c:a', 'aac',
        '-loglevel', 'quiet',
        output_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Created final video: {output_file}")



