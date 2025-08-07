#!/usr/bin/env python3
"""
Test script to verify WebM audio processing with FFmpeg
"""

import subprocess
import tempfile
import os

def test_ffmpeg_webm_conversion():
    """Test FFmpeg WebM to WAV conversion"""
    print("🎤 Testing FFmpeg WebM Audio Processing")
    print("=" * 50)
    
    # Create a simple test audio file (silence)
    try:
        # Create a 1-second silence WebM file
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_webm:
            temp_webm_path = temp_webm.name
        
        # Use FFmpeg to create a test WebM file
        result = subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=mono:sample_rate=16000',
            '-t', '1', '-c:a', 'libopus', temp_webm_path, '-y'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Created test WebM file successfully")
            
            # Test conversion to WAV
            temp_wav_path = temp_webm_path.replace('.webm', '.wav')
            
            result = subprocess.run([
                'ffmpeg', '-i', temp_webm_path, 
                '-acodec', 'pcm_s16le', 
                '-ar', '16000', 
                '-ac', '1', 
                temp_wav_path,
                '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(temp_wav_path):
                print("✅ WebM to WAV conversion successful")
                print(f"   Input: {temp_webm_path}")
                print(f"   Output: {temp_wav_path}")
                
                # Check file sizes
                webm_size = os.path.getsize(temp_webm_path)
                wav_size = os.path.getsize(temp_wav_path)
                print(f"   WebM size: {webm_size} bytes")
                print(f"   WAV size: {wav_size} bytes")
                
                # Clean up
                os.unlink(temp_webm_path)
                os.unlink(temp_wav_path)
                
                print("\n🎯 FFmpeg WebM processing is working correctly!")
                print("   Your voice recording should now work properly.")
                
            else:
                print(f"❌ WebM to WAV conversion failed: {result.stderr}")
                if os.path.exists(temp_webm_path):
                    os.unlink(temp_webm_path)
                    
        else:
            print(f"❌ Failed to create test WebM file: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        # Clean up any temporary files
        try:
            if 'temp_webm_path' in locals() and os.path.exists(temp_webm_path):
                os.unlink(temp_webm_path)
            if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
        except:
            pass

if __name__ == "__main__":
    test_ffmpeg_webm_conversion() 