import os
import unittest
from src.audio_processing.transcriber import load_model, transcribe_audio

class TestTranscriber(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the Whisper model once for all tests to save time."""
        cls.model = load_model("base")

    def test_transcribe_audio(self):
        """Test transcription of a sample audio file."""
        audio_path = 'data/test/audio/Mom 4 - 1.mp3'
        transcribed_text = transcribe_audio(audio_path, self.model)
        
        # Ensure transcribed text is not empty
        self.assertTrue(transcribed_text.strip(), "Transcription is empty.")

    def test_file_not_found(self):
        """Test handling of a non-existing audio file."""
        with self.assertRaises(FileNotFoundError):
            transcribe_audio('non_existent_file.mp3', self.model)

if __name__ == '__main__':
    unittest.main()