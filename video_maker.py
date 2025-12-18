import json, os, sys, subprocess
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx
from PIL import Image
import numpy as np

# Fix for the 2025 Pillow 'ANTIALIAS' error
if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render(plan):
    with open(plan, 'r') as f: data = json.load(f)
    # Generating high-emotion human voice
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", data['script_text'], "--write-media", "v.mp3"])
    
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 2
    bg_music = AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.15).set_duration(duration)
    
    clips = [ColorClip((1080, 1920), (15,5,25), duration=duration)]
    for i, img_path in enumerate(data['card_images']):
        full_path = os.path.join("assets/tarot_cards", img_path)
        if os.path.exists(full_path):
            img = ImageClip(full_path).resize(width=950).set_pos("center").set_start(3 + i*5).set_duration(5).crossfadein(0.5)
            clips.append(img)

    # Branded Website Overlay
    cta = TextClip("thezodiacvault.kesug.com", fontsize=50, color='cyan', font="assets/fonts/Cinzel-Bold.ttf", size=(900, None), method='caption')
    clips.append(cta.set_pos(('center', 1600)).set_start(duration-5).set_duration(5))

    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, bg_music]))
    final.write_videofile(os.path.join("output_videos", data['file_name']), fps=24, preset='ultrafast')

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot')]
    if files: render(max(files, key=os.path.getctime))
