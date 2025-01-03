from moviepy import *


def sync_lyrics_manually(lyrics, video_input_file, video_output_file):
    """ Function to place the text in a simple manner using manual timestamps
    Customisation : font, color, position"""
    video_clip = VideoFileClip(video_input_file)
    text_clips = []

    for start_time, end_time, lyric in lyrics:
        text_clip = TextClip(
            text=lyric,
            font='Helvetica', # use any locally installed font
            color=(255, 255, 255, 255), # RGB, RGBA, Hex, name
            size=(video_clip.w, None)
        )
        text_clip = (text_clip.with_position('center', 'top')
                     .with_duration(end_time - start_time)
                     .with_start(start_time))

        text_clips.append(text_clip)

    if text_clips:
        final_clip = CompositeVideoClip([video_clip] + text_clips)
        final_clip.audio = video_clip.audio
        final_clip.write_videofile(video_output_file, codec='libx264', audio_codec='aac')
        print(f"Video saved to {video_output_file}")
    else:
        print("No lyrics to add, skipping video creation.")



def sync_lyrics_grid_to_video(lyrics_lines, video_file, output_file, grid_size=(5, 12), first_letter_scale=1.8):
    """ Function to place text in a more advanced manner using manual timestamps and a grid layout
        Customisaton :
        grid_size (r X c): ensure minimum # columns = longest word + 1 or letters might be cut off
        first_letter_scale: first letter of each word is scaled
        font : use any locally installed font. trouble shoot by using absolute path
        color : RGB, RGBA, Hex, names
        size : fallback in case method not label
        stroke_width : border thickness
        stroke_color : border color
        method : label (autosized) or caption (absolute size)
        """
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
            first_letter_space = first_letter_scale

            # Total number of cells needed
            word_length_in_cells = first_letter_space + len(word) - 1

            # check space available in row
            if current_col + word_length_in_cells > cols:
                current_col = 0
                current_row += 1

            if current_row >= rows:
                print(f"Warning: No space left in the grid for word: '{word}'. Split list entry further")
                break

            # Place each character in the grid
            for idx, char in enumerate(word):
                if idx == 0:  # First letter
                    char_width = cell_width * first_letter_scale
                else:
                    char_width = cell_width

                x_pos = current_col * cell_width
                y_pos = current_row * cell_height

                # Customisation
                char_clip = TextClip(
                    text=char,
                    font='Futura', # use any locally installed font
                    color=(240, 215, 19, 255), # RGB, RGBA, Hex, name
                    size=(int(char_width)+50, int(cell_height)+50),
                    stroke_width=4,
                    stroke_color=(145, 145, 134),
                    method='label' # autosize letters
                ).with_position((x_pos, y_pos)).with_duration(end_time - start_time).with_start(start_time)

                text_clips.append(char_clip)

                if idx == 0:
                    current_col += first_letter_scale  # Add space for the larger first letter
                else:
                    current_col += 1  # Regular spacing for subsequent letters
            current_col += 1 # blank space after each word

    if text_clips:
        final_clip = CompositeVideoClip([video_clip] + text_clips)
        final_clip.audio = video_clip.audio
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        print(f"Video saved to {output_file}")
    else:
        print("No lyrics to add, skipping video creation.")

