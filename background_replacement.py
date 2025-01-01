import os
import cv2
import numpy as np
import mediapipe as mp
import subprocess

def _enhance_frame(frame):
    """ Internal function to enhance frame using CLAHE
    (Contrast Limited Adaptive Histogram Equalization)"""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l)
    enhanced_lab = cv2.merge((enhanced_l, a, b))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

def _generate_foreground_mask(frame, segmentation_model):
    """ Internal function creating background mask using mediapipe """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = segmentation_model.process(frame_rgb)
    mask = results.segmentation_mask
    _, binary_mask = cv2.threshold(mask, 0.1, 255, cv2.THRESH_BINARY)
    return binary_mask.astype(np.uint8)

def _stabilize_mask(current_mask, previous_mask, alpha=0.8):
    """ Internal function to reduce jittering by weighing previous frame with current """
    if previous_mask is None:
        return current_mask
    return cv2.addWeighted(previous_mask, alpha, current_mask, 1 - alpha, 0)

def _feather_mask(mask, blur_radius=15):
    """ Internal function to blur edges between foreground and background"""
    dilated_mask = cv2.dilate(mask, None, iterations=5)
    blurred_mask = cv2.GaussianBlur(dilated_mask, (blur_radius, blur_radius), 0)
    return blurred_mask.astype(np.uint8)

def _crop_background_to_input_aspect_ratio(background_frame, input_width, input_height):
    """ Internal function to cut background to portrait mode, retaining the original perspective.
    YEA THAT DOESN'T WORK (YET)"""
    bg_height, bg_width, _ = background_frame.shape
    input_aspect_ratio = input_width / input_height
    bg_aspect_ratio = bg_width / bg_height
    # background in landscape
    if bg_aspect_ratio > input_aspect_ratio:
        new_width = int(bg_height * input_aspect_ratio)
        offset = (bg_width - new_width) // 2
        cropped_background = background_frame[:, offset:offset+new_width]
    else:
        new_height = int(bg_width / input_aspect_ratio)
        offset = (bg_height - new_height) // 2
        cropped_background = background_frame[offset:offset+new_height, :]
    cropped_resized_background = cv2.resize(cropped_background, (input_width, input_height))
    return cropped_resized_background


def _replace_background_with_feathering(frame, background_resized, mask):
    """ Internal function to replace background with feathering"""
    feathered_mask = _feather_mask(mask)
    # normalize the feathered mask to create an alpha channel
    alpha = feathered_mask / 255.0
    # expand alpha to have the same number of channels as the frame
    alpha = cv2.merge([alpha, alpha, alpha])  # Convert (H, W, 1) -> (H, W, 3)
    # convert frame and background to float32 for blending
    frame = frame.astype(np.float32)
    background_resized = background_resized.astype(np.float32)
    # Blend the foreground and background using the alpha mask
    foreground = cv2.multiply(alpha, frame, dtype=cv2.CV_32F)
    background = cv2.multiply(1 - alpha, background_resized, dtype=cv2.CV_32F)
    blended_frame = cv2.add(foreground, background)
    return blended_frame.astype(np.uint8)  # Convert back to uint8 for output

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


def process_video_with_video_background(input_path, output_path, background_video_path):
    """ function to replace background """
    temp_video_path = output_path.replace('.mp4', '_temp.mp4')
    # open up original video and background video
    cap = cv2.VideoCapture(input_path)
    background_cap = cv2.VideoCapture(background_video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open input video file: {input_path}")
    if not background_cap.isOpened():
        raise FileNotFoundError(f"Cannot open background video file: {background_video_path}")
    fps = int(cap.get(cv2.CAP_PROP_FPS)) # get frames per second of original video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # get width of original video
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # get height of original video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # prepare output file
    out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    # mediapipe image segmentation (specialised for humans)
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    segmentation_model = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
    previous_mask = None
    for frame_idx in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        ret_bg, background_frame = background_cap.read()
        if not ret_bg:
            background_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_bg, background_frame = background_cap.read()
        background_resized = _crop_background_to_input_aspect_ratio(background_frame, width, height)
        enhanced_frame = _enhance_frame(frame)
        current_mask = _generate_foreground_mask(enhanced_frame, segmentation_model)
        stabilized_mask = _stabilize_mask(current_mask, previous_mask)
        previous_mask = stabilized_mask
        final_frame = _replace_background_with_feathering(frame, background_resized, stabilized_mask)
        out.write(final_frame)

        if frame_idx % 100 == 0:
            print(f"Processed frame {frame_idx + 1}/{total_frames}")
    cap.release()
    background_cap.release()
    out.release()

    _add_audio(input_path, temp_video_path, output_path)
    os.remove(temp_video_path)



def process_all_videos_with_video_background(video_input_background_dir, output_dir, background_video_path):
    """ Iterate through all videos in directory and replace background if necessary"""
    os.makedirs(output_dir, exist_ok=True)
    video_files = [f for f in os.listdir(video_input_background_dir) if f.endswith(('.mp4', '.mov'))]
    for idx, video_file in enumerate(video_files, start=10):
        input_path = os.path.join(video_input_background_dir, video_file)
        output_path = os.path.join(output_dir, f"processed_{idx}.mp4")
        process_video_with_video_background(input_path, output_path, background_video_path)



#if __name__ == "__main__":
    #video_input_background_dir = "/Users/laura/Desktop/DIGCRE/cutVideo"
    #output_dir = "/Users/laura/Desktop/DIGCRE"
    #background_path = "/Users/laura/Desktop/DIGCRE/background_extraction/background_stars.mp4"
    #process_all_videos_with_video_background(video_input_background_dir, output_dir, background_path)
