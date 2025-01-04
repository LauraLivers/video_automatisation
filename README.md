<h1>video automatisation</h1>

<img src="dodji.gif" style="display:inline-block; width: 45%; margin-right: 5%;" />
<img src="dodji.png" style="display:inline-block; width: 45%;" />


_2025 HS DIGCRE - laura livers_

this framework was created as a proof-of-concept semester project   
for the module _Digital Creativity_ at University of Applied Sciences Lucerne  

**Summary**  
This framework is designed to automate various video editing tasks,  
specifically for creating content intended for social media. It is  
aimed at individuals in the creative industry, with a particular focus on musicians




**Setup**  
this code assumes the following conditions are met:
- several takes of the same or similar scene
- each video contains the same background music
- background music is available as soundfile in ideally uncompressed format (eg. wav)

<p>&nbsp;</p>

<h1>Functions</h1>

```adjust_exposure()```  

quick adjustments to lighten or darken the footage  
&nbsp;&nbsp;&nbsp;&nbsp;_brightness_ : takes values between -1 and 1, where 0 represents the original  
&nbsp;&nbsp;&nbsp;&nbsp;_contrast_ : takes values between 0 and 1, where 1.0 represents the original  
&nbsp;&nbsp;&nbsp;&nbsp;_gamma_ : takes values bigger than 0, where 1.0 represents the original  

```apply_teal_orange()```  

hollywood-style filter where shadows become teal and highlights orange
&nbsp;&nbsp;&nbsp;&nbsp;_intensity_: takes values between 0 and 1

```apply_black_white()```  

applies opencv cvtColor to footage  

```shorten_video()```  

&nbsp;&nbsp;&nbsp;&nbsp;_seconds_: creates video of length seconds  

```apply_slow_motion()```  

&nbsp;&nbsp;&nbsp;&nbsp;_slow_down_factor_: takes values between 0 and 1  

```rgb_trail```  

splits video into RGB channels and applies different lags to each, creating a trailing effect  
&nbsp;&nbsp;&nbsp;&nbsp;_red_lag, green_lag, blue_lag_: takes int as frame unit for lag  

```sync_lyrics_manually()```  

places lyrics by default in the center of the video  
&nbsp;&nbsp;&nbsp;&nbsp;_lyrics_: (start, end, 'lyrics')
&nbsp;&nbsp;&nbsp;&nbsp;_color_: RGB, RGBA, Hex format  

```sync_lyrics_grid_to_video()```  

places lyrics within imaginary grid and scales first letter of each word  
&nbsp;&nbsp;&nbsp;&nbsp;_color_: RGB, RGBA, Hex format  
&nbsp;&nbsp;&nbsp;&nbsp;_grid_size_: (row, col) ensure col is at least longest_word + 1  
&nbsp;&nbsp;&nbsp;&nbsp;_first_letter_scale_: float  


**use in sequence**  
```extract_beats_from_song()```   

uses librosa.beat_track to create a beat_sequence  

```cut_videos_by_song_beats()```  

correlates each video with the beat_sequence to cut at the same point  
relative to the original audio file  

```concatenate_clips_randomly```  

reconstructs the beat_sequence in order, randomly shuffly the takes  
  
  

```process_video_with_video_background()```  

uses [Google Mediapipe](https://github.com/google-ai-edge/mediapipe) to detect background   
and replaces it with another background video  
the internal functions are to stabilize the mask and feather the edges  

