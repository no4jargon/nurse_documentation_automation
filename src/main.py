# main.py

import os
from src.audio_processing.audio_cleaning import reduce_noise
from src.audio_processing.transcriber import load_model, transcribe_audio, save_transcription
from src.text_processing.chunker import chunk_transcription, save_chunks
from src.text_processing.process_form import process_json_file
from src.form_filling.form_filler import fill_form_from_chunks, save_filled_form
from src.metrics.compare import compare

def get_next_transcription_file_name(audio_file_path, transcriptions_folder) -> str:
    """
    Determines the next available file name for saving a transcription based on the audio file's basename.
    
    Args:
        audio_file_path (str): The path to the audio file.
        transcriptions_folder (str): The path to the folder where transcriptions are stored.
    
    Returns:
        str: The next file name in the sequence (e.g., 'audiofile_1.txt' if 'audiofile_0.txt' exists).
    """
    # Extract the basename from the audio file path
    basename = os.path.splitext(os.path.basename(audio_file_path))[0]
    
    # List all files in the transcriptions folder
    files = os.listdir(transcriptions_folder)
    
    # Filter only files that match the pattern '{basename}_#.txt'
    file_indices = [
        int(file.split('_')[1].split('.')[0])
        for file in files if file.startswith(f"{basename}_") and file.endswith('.txt')
    ]
    
    # Determine the next index
    existing_index = max(file_indices) if file_indices else 0
    
    # Return the next file name in the format '{basename}_{existing_index+1}'
    return f"{basename}_{existing_index + 1}"

def main():
    audio_file_path = input("Enter the path to the audio file: ").strip().strip("'")
    if not os.path.exists(audio_file_path):
        print(f"Error: The file '{audio_file_path}' does not exist.")
        return
    if "data/test" in audio_file_path:
        root = "data/test"
    else:
        root = "data/trials"
    transcriptions_folder = os.path.join(root, "transcriptions");os.makedirs(transcriptions_folder, exist_ok=True)
    chunks_folder = os.path.join(root, "chunks");os.makedirs(chunks_folder, exist_ok=True)
    filled_form_folder = os.path.join(root, "filled_forms");os.makedirs(chunks_folder, exist_ok=True)
    saved_files_base_name = get_next_transcription_file_name(audio_file_path, transcriptions_folder)

    # Step 2: Clean the audio
    # cleaned_audio_path = "cleaned_audio.wav"  # Temporary path to save cleaned audio
    # reduce_noise(audio_file_path, cleaned_audio_path)
    # print(f"Cleaned audio saved to: {cleaned_audio_path}")

    model = load_model("large")

    transcribed_text = transcribe_audio(audio_file_path, model)
    print(f"Transcribed Text: {transcribed_text}")
    transcription_file_path = os.path.join(transcriptions_folder, f"{saved_files_base_name}.txt")
    save_transcription(transcribed_text, transcription_file_path)
    print(f"Transcription saved to: {transcription_file_path}")
    try:
        transcription_comparison = compare(transcription_file_path, "transcriptions")
    except:
        pass

    chunked_output = chunk_transcription(transcribed_text)
    print(f"Chunked Output: {chunked_output}")
    chunks_file_path = os.path.join(chunks_folder, f"{saved_files_base_name}.json")
    save_chunks(chunked_output, chunks_file_path)
    print(f"Chunks saved to: {chunks_file_path}")
    try:
        chunk_comparison = compare(chunks_file_path, "chunks")
    except:
        pass

    form_dataframe = process_json_file("./form.json")
    filled_rows = fill_form_from_chunks(form_dataframe, chunked_output)
    print(f"Filled rows: {filled_rows}")
    filled_form_file_path = os.path.join(filled_form_folder, f"{saved_files_base_name}.json")
    save_filled_form(filled_rows, filled_form_file_path)
    print(f"Chunks saved to: {chunks_file_path}")
    try:
        filled_forms_comparison = compare(filled_form_file_path, "filled_forms")
    except:
        pass
    breakpoint()


if __name__ == "__main__":
    main()