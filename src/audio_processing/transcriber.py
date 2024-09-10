# transcriber.py
from openai import OpenAI
import whisper
import os

def load_model(model_name: str = "large"):
    """
    Load the Whisper model for transcription.
    Args:
        model_name (str): The model variant to load ('tiny', 'base', 'small', 'medium', 'large').
    Returns:
        model: The Whisper model object.
    """
    print(f"Loading Whisper model: {model_name}...")
    model = whisper.load_model(model_name)
    print("Model loaded successfully.")
    return model

def transcribe_audio(file_path: str, model):
    """
    Transcribe an audio file to text using the Whisper model.
    Args:
        file_path (str): Path to the audio file.
        model: Loaded Whisper model.
    Returns:
        str: The transcribed text.
    """
    print(f"Transcribing audio file: {file_path}...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    result = model.transcribe(file_path)
    text = result["text"]
    print("Transcription completed.")
    return text

def save_transcription(text: str, output_file: str):
    """
    Save the transcribed text to a file.
    Args:
        text (str): The transcribed text.
        output_file (str): Path to the output text file.
    """
    with open(output_file, 'w') as file:
        file.write(text)
    print(f"Transcription saved to {output_file}")

def main():
    # Example usage
    model = load_model("base")
    audio_file_path = "path/to/audio/file.wav"  # Replace with your audio file path
    transcription = transcribe_audio(audio_file_path, model)
    save_transcription(transcription, "transcriptions/output.txt")

if __name__ == "__main__":
    main()