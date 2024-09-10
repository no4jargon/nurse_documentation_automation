# broken
# audio_cleaning.py
from pydub import AudioSegment
import noisereduce as nr
import numpy as np
import os
import librosa

def load_audio(file_path: str):
    """
    Load an audio file using pydub.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        AudioSegment: The loaded audio segment.
    """
    print(f"Loading audio file: {file_path}...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    audio = AudioSegment.from_file(file_path)
    print("Audio loaded successfully.")
    return audio

def reduce_noise(file_path: str, output_file: str):
    """
    Perform noise reduction on an audio file.
    Args:
        file_path (str): Path to the input audio file.
        output_file (str): Path to save the noise-reduced audio file.
    """
    print(f"Performing noise reduction on: {file_path}...")

    # Load audio file with librosa
    y, sr = librosa.load(file_path, sr=None)

    # Perform noise reduction
    reduced_noise = nr.reduce_noise(y=y, sr=sr)

    # Convert back to AudioSegment for exporting
    audio_reduced = AudioSegment(
        reduced_noise.tobytes(), 
        frame_rate=sr,
        sample_width=reduced_noise.dtype.itemsize, 
        channels=1
    )

    # Export noise-reduced audio
    audio_reduced.export(output_file, format="wav")
    print(f"Noise-reduced audio saved to {output_file}")

def save_audio(audio: AudioSegment, output_path: str):
    """
    Save an AudioSegment object to a file.
    Args:
        audio (AudioSegment): The audio segment to save.
        output_path (str): Path to the output file.
    """
    audio.export(output_path, format='wav')
    print(f"Audio saved to {output_path}")

def main():
    # Example usage
    input_file_path = "path/to/audio/file.wav"  # Replace with your input audio file path
    output_file_path = "cleaned_audio.wav"
    reduce_noise(input_file_path, output_file_path)

if __name__ == "__main__":
    main()