import speech_recognition as sr
import pyttsx3
import os
import tempfile
import wave
import numpy as np
from datetime import datetime
import json
import base64
import io

class AudioProcessor:
    def __init__(self):
        """Initialize audio processing components"""
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        # Configure text-to-speech engine
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume level
        
        # Get available voices and set a default
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        
        # Create audio directory if it doesn't exist
        self.audio_dir = "audio_files"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def speech_to_text(self, audio_data=None, audio_file_path=None):
        """
        Convert speech to text using Google Speech Recognition
        
        Args:
            audio_data: Base64 encoded audio data
            audio_file_path: Path to audio file
            
        Returns:
            dict: {'success': bool, 'text': str, 'error': str}
        """
        try:
            if audio_data:
                # Decode base64 audio data
                if ',' in audio_data:
                    # Remove data URL prefix
                    audio_data = audio_data.split(',')[1]
                
                audio_bytes = base64.b64decode(audio_data)
                
                # Try multiple approaches to process the audio
                return self._process_audio_data(audio_bytes)
                
            elif audio_file_path:
                with sr.AudioFile(audio_file_path) as source:
                    audio_source = self.recognizer.record(source)
                return self._recognize_speech(audio_source)
            else:
                return {'success': False, 'text': '', 'error': 'No audio data provided'}
            
        except Exception as e:
            return {'success': False, 'text': '', 'error': f'Error processing audio: {str(e)}'}
    
    def _process_audio_data(self, audio_bytes):
        """Process audio data with multiple fallback methods"""
        import io
        import wave
        import tempfile
        import os
        
        # Method 1: Try to read as WAV
        try:
            with io.BytesIO(audio_bytes) as audio_io:
                with wave.open(audio_io, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    sample_rate = wav_file.getframerate()
                    sample_width = wav_file.getsampwidth()
                    
                    audio_source = sr.AudioData(frames, sample_rate, sample_width)
                    return self._recognize_speech(audio_source)
        except Exception as e:
            print(f"WAV processing failed: {e}")
        
        # Method 2: Try to convert WebM to WAV using ffmpeg
        try:
            # Save the audio bytes to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_webm:
                temp_webm.write(audio_bytes)
                temp_webm_path = temp_webm.name
            
            # Convert to WAV using ffmpeg
            temp_wav_path = temp_webm_path.replace('.webm', '.wav')
            
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', temp_webm_path, 
                '-acodec', 'pcm_s16le', 
                '-ar', '16000', 
                '-ac', '1', 
                temp_wav_path,
                '-y'  # Overwrite output file
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_wav_path):
                # Read the converted WAV file
                with sr.AudioFile(temp_wav_path) as source:
                    audio_source = self.recognizer.record(source)
                
                # Clean up temporary files
                os.unlink(temp_webm_path)
                os.unlink(temp_wav_path)
                
                return self._recognize_speech(audio_source)
            else:
                print(f"FFmpeg conversion failed: {result.stderr}")
                # Clean up temporary files
                if os.path.exists(temp_webm_path):
                    os.unlink(temp_webm_path)
                if os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
                    
        except Exception as e:
            print(f"WebM conversion failed: {e}")
            # Clean up any temporary files
            try:
                if 'temp_webm_path' in locals() and os.path.exists(temp_webm_path):
                    os.unlink(temp_webm_path)
                if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
            except:
                pass
        
        # Method 3: Try as raw audio with common settings (fallback)
        try:
            # Common audio settings for WebM/Opus
            sample_rate = 16000
            sample_width = 2  # 16-bit
            
            audio_source = sr.AudioData(audio_bytes, sample_rate, sample_width)
            return self._recognize_speech(audio_source)
        except Exception as e:
            print(f"Raw audio processing failed: {e}")
        
        # Method 4: Try different sample rates
        for sample_rate in [8000, 16000, 22050, 44100]:
            try:
                audio_source = sr.AudioData(audio_bytes, sample_rate, 2)
                result = self._recognize_speech(audio_source)
                if result['success']:
                    return result
            except Exception as e:
                continue
        
        return {'success': False, 'text': '', 'error': 'Could not process audio format. Please try recording again.'}
    
    def _recognize_speech(self, audio_source):
        """Recognize speech from audio source"""
        # Configure recognizer for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        try:
            text = self.recognizer.recognize_google(audio_source, language='en-US')
            if text.strip():
                return {'success': True, 'text': text.strip(), 'error': None}
            else:
                return {'success': False, 'text': '', 'error': 'No speech detected'}
        except sr.UnknownValueError:
            return {'success': False, 'text': '', 'error': 'Could not understand audio. Please speak more clearly.'}
        except sr.RequestError as e:
            return {'success': False, 'text': '', 'error': f'Speech recognition service error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'text': '', 'error': f'Recognition error: {str(e)}'}
    
    def text_to_speech(self, text, save_to_file=True):
        """
        Convert text to speech and optionally save to file
        
        Args:
            text: Text to convert to speech
            save_to_file: Whether to save audio to file
            
        Returns:
            dict: {'success': bool, 'audio_file': str, 'error': str}
        """
        try:
            if save_to_file:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_file = os.path.join(self.audio_dir, f"response_{timestamp}.wav")
                
                # Save speech to file
                self.engine.save_to_file(text, audio_file)
                self.engine.runAndWait()
                
                return {
                    'success': True, 
                    'audio_file': audio_file,
                    'error': None
                }
            else:
                # Just speak without saving
                self.engine.say(text)
                self.engine.runAndWait()
                return {'success': True, 'audio_file': None, 'error': None}
                
        except Exception as e:
            return {'success': False, 'audio_file': None, 'error': f'Error in text-to-speech: {str(e)}'}
    
    def get_audio_base64(self, audio_file_path):
        """
        Convert audio file to base64 string for web transmission
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            str: Base64 encoded audio data
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
                return f"data:audio/wav;base64,{base64_audio}"
        except Exception as e:
            print(f"Error converting audio to base64: {str(e)}")
            return None
    
    def cleanup_old_audio_files(self, max_age_hours=24):
        """
        Clean up old audio files to save disk space
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.audio_dir):
                file_path = os.path.join(self.audio_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    age_hours = (current_time - file_time).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        os.remove(file_path)
                        print(f"Cleaned up old audio file: {filename}")
        except Exception as e:
            print(f"Error cleaning up audio files: {str(e)}")
    
    def get_audio_info(self, audio_file_path):
        """
        Get information about an audio file
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            dict: Audio file information
        """
        try:
            with wave.open(audio_file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                
                return {
                    'frames': frames,
                    'rate': rate,
                    'duration': duration,
                    'channels': wav_file.getnchannels(),
                    'sample_width': wav_file.getsampwidth()
                }
        except Exception as e:
            return {'error': str(e)}

# Test function
def test_audio_processor():
    """Test the audio processor functionality"""
    processor = AudioProcessor()
    
    print("🎤 Audio Processor Test")
    print("=" * 30)
    
    # Test text-to-speech
    test_text = "Hello! This is a test of the audio processor."
    print(f"Testing text-to-speech with: '{test_text}'")
    
    result = processor.text_to_speech(test_text, save_to_file=True)
    if result['success']:
        print(f"✅ Text-to-speech successful: {result['audio_file']}")
        
        # Test audio info
        info = processor.get_audio_info(result['audio_file'])
        print(f"📊 Audio info: {info}")
        
        # Test base64 conversion
        base64_audio = processor.get_audio_base64(result['audio_file'])
        if base64_audio:
            print(f"✅ Base64 conversion successful (length: {len(base64_audio)})")
        else:
            print("❌ Base64 conversion failed")
    else:
        print(f"❌ Text-to-speech failed: {result['error']}")
    
    print("\n🧹 Cleaning up old audio files...")
    processor.cleanup_old_audio_files()
    print("✅ Test completed!")

if __name__ == "__main__":
    test_audio_processor() 