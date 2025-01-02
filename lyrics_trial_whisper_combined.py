import pandas as pd
import whisper
import re
from moviepy import *
import syllapy  # Library to split text into syllables


def _load_lyrics(csv_file, song_id):
    lyrics_df = pd.read_csv(csv_file, header=None, names=['id', 'lyric'])
    song_id_formatted = f"id_{song_id}"
    song_lyrics = lyrics_df.loc[lyrics_df['id'] == song_id_formatted]
    if song_lyrics.empty:
        print(f"No lyrics found for song_id {song_id_formatted}.")
    else:
        print(f"Lyrics for song_id {song_id_formatted}:\n", song_lyrics)
    song_lyrics.loc[:, 'language'] = song_lyrics['lyric'].apply(
        lambda x: re.search(r'<(.*?)>', x).group(1) if re.search(r'<(.*?)>', x) else None)
    song_lyrics.loc[:, 'lyric'] = song_lyrics['lyric'].apply(lambda x: re.sub(r'<.*?>', '', x).strip())
    return song_lyrics

# Function to detect vocal segments with Whisper (including word-level timestamps)
def _detect_vocal_segments_with_whisper(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, word_timestamps=True, language='de')  # Adjust language code as needed
    timestamps = []
    for segment in result['segments']:
        for word_info in segment['words']:
            timestamps.append((word_info['start'], word_info['end'], word_info['word']))
    return timestamps


def _split_into_syllables(lyric):
    try:
        syllables = syllapy._syllables(lyric)
        if isinstance(syllables, list):
            return syllables
        else:
            raise ValueError(f"Expected list of syllables, but got {type(syllables)}: {syllables}")
    except Exception as e:
        print(f"Error splitting lyric '{lyric}' into syllables: {e}")

        # Fallback: Try manual split if syllapy fails
        syllables = _manual_split_into_syllables(lyric)
        if not syllables:
            print(f"No syllables found for lyric '{lyric}', skipping it.")
        return syllables

def _manual_split_into_syllables(lyric):
    # Heuristic split: simple space-based or vowel grouping (basic rule-based split)
    if len(lyric) < 3:
        return [lyric]  # Treat as a single syllable
    syllables = re.findall(r'[^aeiou]*[aeiou]+[^aeiou]*', lyric)  # Simple vowel-based split
    return syllables or [lyric]

def _match_lyrics_to_speech(lyrics_df, timestamps):
    matched_lyrics = []
    all_lyrics = lyrics_df['lyric'].tolist()
    lyric_idx = 0
    timestamp_idx = 0

    while lyric_idx < len(all_lyrics) and timestamp_idx < len(timestamps):
        lyric = all_lyrics[lyric_idx]

        # Calculate start and end times for the current lyric
        num_words = len(lyric.split())
        start_time = timestamps[timestamp_idx][0]
        end_time = timestamps[min(timestamp_idx + num_words - 1, len(timestamps) - 1)][1]

        # Add matched lyric
        matched_lyrics.append((start_time, end_time, lyric))

        # Move to the next lyric and update timestamp index
        timestamp_idx += num_words
        lyric_idx += 1

    # Ensure all lyric lines are processed
    while lyric_idx < len(all_lyrics):
        print(f"Warning: No matching timestamps found for lyric: '{all_lyrics[lyric_idx]}'.")
        lyric_idx += 1

    print("Matched Lyrics with Timestamps:", matched_lyrics)
    return matched_lyrics


def _sync_lyrics_to_video(matched_lyrics, video_file, output_file):
    video_clip = VideoFileClip(video_file)
    text_clips = []
    second_text_clips = []  # For the second set of lyrics (with different color and position)

    for start_time, end_time, lyric in matched_lyrics:
        # First text clip (original)
        text_clip = TextClip(text=lyric,
                             font='Helvetica',
                             color=(255, 255, 255, 255),
                             size=(video_clip.w, None))
        text_clip = (text_clip.with_position('center', 'top')).with_duration(end_time - start_time).with_start(
            start_time)

        # Second text clip (different color and position)
        second_text_clip = TextClip(text=lyric, font='Helvetica', color=(192, 192, 192, 128), size=(video_clip.w, None))
        second_text_clip = (second_text_clip.with_position('center', 'bottom')).with_duration(
            end_time - start_time).with_start(start_time)  # Slightly lower and to the right

        text_clips.append(text_clip)
        second_text_clips.append(second_text_clip)

    if text_clips:
        # Combine both the original and second set of text clips
        final_clip = CompositeVideoClip([video_clip] + text_clips + second_text_clips)
        final_clip.audio = video_clip.audio  # Retain original audio
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        print(f"Video saved to {output_file}")
    else:
        print("No text clips to add, skipping video creation.")



def process_audio_video(csv_file, song_id, audio_file, video_file, output_file):
    lyrics_df = _load_lyrics(csv_file, song_id)
    timestamps = _detect_vocal_segments_with_whisper(audio_file)
    matched_lyrics = _match_lyrics_to_speech(lyrics_df, timestamps)
    _sync_lyrics_to_video(matched_lyrics, video_file, output_file)


# Example usage:
#song_id = 1
#csv_file = "/Users/laura/Desktop/DIGCRE/Lyrics/lyrics_data.csv"  # Your lyrics CSV file
#audio_file = '/Users/laura/Desktop/DIGCRE/Lyrics/vocals_output_finetuned.wav'  # Extracted vocals
#video_file = "/Users/laura/Desktop/DIGCRE/processed_10.mp4"  # Your video file
#output_file = "lyrics8.mp4"  # The output video file with synced lyrics

#process_audio_video(csv_file, song_id, audio_file, video_file, output_file)



