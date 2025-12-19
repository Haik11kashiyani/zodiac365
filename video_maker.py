import json, os, subprocess, random, re
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from PIL import Image
import numpy as np

# System Font Fix
FONT_PATH = "Cinzel-Bold" 

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def clean_filename(filename):
    """Removes illegal characters like : ? < > | * for GitHub/Windows compatibility."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def apply_smooth_zoom(clip, duration):
    """Titan Engine: Smoothly zooms from 1.0x to 1.08x for professional motion."""
    return clip.resize(lambda t: 1 + 0.08 * (t/duration)).set_duration(duration)

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    # Sanitize the filename immediately
    safe_title = clean_filename(data['title']).replace(" ", "_")
    output_name = f"{safe_title}.mp4"
    print(f"🔱 TITAN 2.1 RENDERING: {output_name}")

    # 1. Generate High-Emotion Voice (Neural Christopher)
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", data['script_text'], "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 1.5
    
    # 2. Base Cinematic Layers
    bg = ColorClip((1080, 1920), (10, 5, 20), duration=duration)
    music = AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.12).set_duration(duration)
    
    clips = [bg]
    
    # 3. Dynamic Visual Engine (Ken Burns)
    imgs = data.get('images', [])
    if imgs:
        time_per_img = duration / len(imgs)
        for i, path in enumerate(imgs):
            if os.path.exists(path):
                img_clip = ImageClip(path).resize(width=1080).set_pos("center")
                img_clip = apply_smooth_zoom(img_clip, time_per_img)
                img_clip = img_clip.set_start(i * time_per_img).crossfadein(0.8).crossfadeout(0.8)
                clips.append(img_clip)

    # 4. KINETIC TYPOGRAPHY (Word-by-Word Professional Sync)
    words = data['script_text'].split()
    chunk_size = 2 # TikTok 'Peak' standard
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    chunk_duration = duration / len(chunks)
    for i, chunk in enumerate(chunks):
        txt = TextClip(chunk.upper(), fontsize=110, color='#FFD700', font=FONT_PATH, 
                       stroke_color='black', stroke_width=4, method='caption', size=(950, None))
        
        txt = txt.set_start(i * chunk_duration).set_duration(chunk_duration).set_pos(('center', 1000))
        txt = txt.fadein(0.2).resize(lambda t: 1 + 0.05 * t)
        clips.append(txt)

    # 5. Permanent Brand & CTA
    brand = TextClip("thezodiacvault.kesug.com", fontsize=40, color='cyan', font=FONT_PATH)
    clips.append(brand.set_pos(('center', 1750)).set_duration(duration).set_opacity(0.7))

    # 6. Final Master Mix
    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, music]))
    final.write_videofile(os.path.join("output_videos", output_name), fps=24, preset='ultrafast', threads=4)

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    # Clean up old plans to prevent accidental repeats
    plans = [f for f in os.listdir('.') if f.startswith('plan_')]
    for p in plans: render(p)
