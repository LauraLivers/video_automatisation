from moviepy import *





def sync_lyrics_manually(lyrics, video_input_file, video_output_file):
    """ Function to place the text in a simple manner using manual timestamps"""
    video_clip = VideoFileClip(video_input_file)
    text_clips = []

    for start_time, end_time, lyric in lyrics:
        text_clip = TextClip(
            text=lyric,
            font='Helvetica',
            color=(255, 255, 255, 255),
            size=(video_clip.w, None)
        )
        text_clip = (text_clip.with_position('center', 'top')
                     .with_duration(end_time - start_time)
                     .with_start(start_time))

        text_clips.append(text_clip)

    if text_clips:
        final_clip = CompositeVideoClip([video_clip] + text_clips)
        final_clip.audio = video_clip.audio  # Retain original audio
        final_clip.write_videofile(video_output_file, codec='libx264', audio_codec='aac')
        print(f"Video saved to {video_output_file}")
    else:
        print("No lyrics to add, skipping video creation.")



def sync_lyrics_grid_to_video(lyrics_lines, video_file, output_file, grid_size=(5, 12), first_letter_scale=1.8):

    # Load the video
    video_clip = VideoFileClip(video_file)
    video_width, video_height = video_clip.w, video_clip.h

    # Calculate grid cell dimensions
    rows, cols = grid_size
    cell_width = video_width / cols
    cell_height = video_height / rows

    text_clips = []

    for start_time, end_time, lyric_line in lyrics_lines:
        words = lyric_line.split()  # Split lyric into words
        current_row = 0
        current_col = 0

        for word in words:
            # Reserve space for the first letter
            first_letter_space = first_letter_scale  # First letter occupies scaled cells

            # Calculate total cells needed for the word
            word_length_in_cells = first_letter_space + len(word) - 1

            # Check if the word fits in the current row, otherwise move to the next row
            if current_col + word_length_in_cells > cols:
                current_col = 0
                current_row += 1

            # Stop if grid is full
            if current_row >= rows:
                print(f"Warning: No space left in the grid for word: '{word}'")
                break

            # Place each character in the grid
            for idx, char in enumerate(word):
                # Calculate character size and position
                if idx == 0:  # First letter
                    char_width = cell_width * first_letter_scale
                else:  # Subsequent letters
                    char_width = cell_width

                # Calculate position
                x_pos = current_col * cell_width
                y_pos = current_row * cell_height

                # Ensure the character fills its grid cell
                char_clip = TextClip(
                    text=char,
                    font='Helvetica',
                    color=(240, 215, 19, 255),
                    size=(int(char_width)+50, int(cell_height)+50),
                    stroke_width=4,
                    stroke_color=(145, 145, 134)
                ).with_position((x_pos, y_pos)).with_duration(end_time - start_time).with_start(start_time)

                text_clips.append(char_clip)

                # Update current column, accounting for first letter width
                if idx == 0:
                    current_col += first_letter_scale  # Add space for the larger first letter
                else:
                    current_col += 1  # Regular spacing for subsequent letters

            # Add a blank cell after the word
            current_col += 1

        # Combine text clips with the video
    if text_clips:
        final_clip = CompositeVideoClip([video_clip] + text_clips)
        final_clip.audio = video_clip.audio  # Retain original audio
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        print(f"Video saved to {output_file}")
    else:
        print("No lyrics to add, skipping video creation.")


lyrics = [
    (6.0, 12, "ah"),
    (12.0, 15.0, 'I bi Wassermasse, stoubtroche'),
    (15.5, 18.5, 'I bi Höllequal, heilige Gral'),
    (18.7, 20.9, 'I bi iisfall, Hitzestau'),
    (21, 24.7, 'I bi Liebi, Liecht, Hass Niid'),
    (25, 30.6, 'I bi Wäutwiit niemert im Nüüt'),
    (31, 34.0, 'I bi aus immer itzt u nie'),
    (34.2 , 38, 'zur gliiche Ziit, vertrou mer blind'),
]

#sync_lyrics_manually(lyrics ,'04 video_output_effects_rgb2.mp4', '05 video_output_lyrics_manually.mp4')

sync_lyrics_grid_to_video(lyrics, '04 video_output_effects_rgb2.mp4', '05 video_output_lyrics_manually6.mp4')