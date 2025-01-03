import subprocess


def shorten_video_seconds(input_video_path, output_video_path):
    """ Creates a copy of the video shortened to -t , 'x' """
    command = [
        "ffmpeg",
        "-y",
        "-i", input_video_path,
        "-t", "90",  # output length in seconds
        "-c:v", "copy",
        "-c:a", "copy",
        output_video_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr.decode('utf-8')}")

    print(f"First 60 seconds of the video with audio saved to: {output_video_path}")


#input_video = "01 cut_video.mp4"
#output_video = "output_video_40s.mp4"
#shorten_video_seconds(input_video, output_video)
