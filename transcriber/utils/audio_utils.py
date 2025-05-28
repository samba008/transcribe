from moviepy.editor import VideoFileClip
import os

def extract_audio(file_path):
    name, _ = os.path.splitext(os.path.basename(file_path))
    audio_path = f'media/{name}.wav'
    video = VideoFileClip(file_path)
    video.audio.write_audiofile(audio_path)
    return audio_path
