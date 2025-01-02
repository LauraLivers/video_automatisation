import torch
import openunmix
from openunmix.utils import preprocess
import librosa
import numpy as np
import soundfile as sf

def separate_vocals(input_audio, output_audio, voc_start):
    """ Function to separate vocals from instruments using openUnmix.
        voc_start   : first appearance of vocals in seconds """
    audio, sr = librosa.load(input_audio, sr=None, mono=False)  # Use input's sample rate
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=0)  # Convert mono to stereo

    # Mask beginning until vocals start to help unmix
    start_sample = int(voc_start * sr)
    vocal_mask = np.ones(audio.shape[1], dtype=np.float32)
    vocal_mask[:start_sample] = 0
    masked_audio = audio * vocal_mask

    # Convert to PyTorch tensor
    audio_tensor = torch.tensor(masked_audio, dtype=torch.float32)
    processed_audio = preprocess(audio_tensor)

    # Perform separation
    separator = openunmix.umxl()
    estimates = separator(processed_audio)

    # Extract vocals and save output
    vocals = estimates[0, 0, :, :].detach().cpu().numpy()  # Shape: (samples, channels)
    sf.write(output_audio, vocals.T, sr)  # .T ensures correct shape for writing

