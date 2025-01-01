from video_cutting import extract_beats_from_song, cut_videos_by_song_beats, concatenate_clips_randomly

import os



def main():

    # DO NOT CHANGE THIS: set working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # PATHS
    audio_file = "01 audio_input/Dodji_feat Laura Livers.wav" # add correct song name
    video_folder = "02 video_input" # place all raw videos in this folder
    output_dir = "03 video_output_cut/" # CHECK THIS::::::
    final_output = os.path.join(output_dir, "cut_video.mp4")


    # 01 extract beat sequence from the song
    print("Analyzing song file...")
    beat_sequence = extract_beats_from_song(audio_file)

    # 02 cut videos based on beat sequence
    print("Cutting videos based on beat sequence...")
    clips_by_beat = cut_videos_by_song_beats(video_folder, beat_sequence, audio_file, output_dir)


    # 03 concatenate random clips into the final video
    print("Combining clips into final video...")
    concatenate_clips_randomly(clips_by_beat, beat_sequence, final_output)

    # 03.2 repeat 03 if result is displeasing. If all versions should be persistent:
    # don't forget to change the name of final_output variable!










if __name__ == '__main__':
    main()