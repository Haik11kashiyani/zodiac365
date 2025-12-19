import json, os, subprocess, random, re
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image
import numpy as np

# System Font Fix
FONT_PATH = "Cinzel-Bold" 

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def clean_for_speech(text):
    """Removes hashtags, asterisks, and meta-tags before TTS speaks them."""
    text = re.sub(r'#\w+', '', text) # Remove hashtags
    text = re.sub(r'\*+', '', text)  # Remove asterisks
    return text.strip()

def apply_camera_path(clip, duration, index):
    """God-Mode Camera: Alternates Zoom-In, Zoom-Out, and Panning."""
    paths = [
        lambda t: 1 + 0.1 * (t/duration),    # Deep Zoom In
        lambda t: 1.1 - 0.1 * (t/duration),  # Slow Pull Out
        lambda t: 1.05                       # Static with slight scale
    ]
    selected_path = paths[index % len(paths)]
    return clip.resize(selected_path).set_duration(duration)

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")
    print(f"🔱 GOD-MODE RENDERING: {safe_title}")

    # 1. Slowed Neural Voice (-10% rate for mystical feel)
    clean_text = clean_for_speech(data['script_text'])
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--rate=-10%", "--text", clean_text, "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 1.0
    
    # 2. Layered Atmosphere
    bg = ColorClip((1080, 1920), (10, 5, 20), duration=duration)
    music = AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.12).set_duration(duration)
    clips = [bg]
    
    # 3. Dynamic Visual Slice Engine
    imgs = data.get('images', [])
    if not imgs: # Fallback for birthday/special if images are missing
        imgs = [os.path.join("assets/zodiac_signs", "Pisces.jpg")] # Default mystical placeholder
        
    num_slices = 4 if len(imgs) == 1 else len(imgs)
    time_per_slice = duration / num_slices
    
    for i in range(num_slices):
        img_path = imgs[i % len(imgs)]
        if os.path.exists(img_path):
            img_clip = ImageClip(img_path).resize(width=1080).set_pos("center")
            # Apply alternating camera paths for peak movement
            img_clip = apply_camera_path(img_clip, time_per_slice, i)
            img_clip = img_clip.set_start(i * time_per_slice).crossfadein(0.5).crossfadeout(0.5)
            clips.append(img_clip)

    # 4. KINETIC TYPOGRAPHY (Perfectly Synced Chunks)
    words = clean_text.split()
    chunk_size = 2 # Best for modern viral retention
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    chunk_dur = duration / len(chunks)
    
    for i, chunk in enumerate(chunks):
        txt = TextClip(chunk.upper(), fontsize=110, color='#FFD700', font=FONT_PATH, 
                       stroke_color='black', stroke_width=4, method='caption', size=(950, None))
        txt = txt.set_start(i * chunk_dur).set_duration(chunk_dur).set_pos(('center', 1100))
        txt = txt.fadein(0.1).resize(lambda t: 1 + 0.03 * t) # Subtle pop
        clips.append(txt)

    # 5. Professional Branding
    brand = TextClip("thezodiacvault.kesug.com", fontsize=40, color='cyan', font=FONT_PATH)
    clips.append(brand.set_pos(('center', 1780)).set_duration(duration).set_opacity(0.6))

    # 6. Final Export
    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, music]))
    final.write_videofile(os.path.join("output_videos", f"{safe_title}.mp4"), fps=24, preset='ultrafast', threads=4)

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    for p in [f for f in os.listdir('.') if f.startswith('plan_')]: render(p)
