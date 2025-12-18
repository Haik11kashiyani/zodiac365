import json, os, subprocess, random
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image
import numpy as np

# System Font Fix
FONT_PATH = "Cinzel-Bold" # Uses the system-registered font from our last fix

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def create_particles(duration):
    """Creates a mystical moving gold dust overlay."""
    def make_frame(t):
        frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        for _ in range(15):
            x = int(540 + 400 * np.sin(t + random.random()))
            y = int(960 + 800 * np.cos(t * 0.5 + random.random()))
            frame[y-5:y+5, x-5:x+5] = [255, 215, 0] # Gold particles
        return frame
    return VideoClip(make_frame, duration=duration).set_opacity(0.3)

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    print(f"🎬 ULTIMATE RENDER: {data['file_name']}")

    # 1. High-Emotion Neural Voice
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", data['script_text'], "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 1.5
    
    # 2. Cinematic Base Layer
    bg = ColorClip((1080, 1920), (10, 5, 20), duration=duration)
    clips = [bg, create_particles(duration)]
    
    # 3. Dynamic Visuals (Ken Burns Effect)
    imgs = data.get('images', [])
    if imgs:
        for i, path in enumerate(imgs):
            if os.path.exists(path):
                img = ImageClip(path).resize(width=1150).set_pos("center")
                # Add slow zoom-in
                img = img.resize(lambda t: 1 + 0.03*t).set_start(0.5 + i*4).set_duration(duration - 1).crossfadein(1)
                clips.append(img)

    # 4. Kinetic Subtitles (Peak Level Typography)
    for i, ol in enumerate(data.get('overlays', [])):
        txt_val = ol['text'].upper()
        # Create a gold text with a deep shadow
        txt = TextClip(txt_val, fontsize=90, color='#FFD700', font=FONT_PATH, stroke_color='black', stroke_width=3, method='caption', size=(900, None))
        
        # Staggered timing based on the list
        start_time = (duration / len(data['overlays'])) * i
        txt = txt.set_pos(('center', 800)).set_start(start_time).set_duration(3).crossfadein(0.3)
        clips.append(txt)

    # 5. Permanent Brand Overlay
    brand = TextClip("thezodiacvault.kesug.com", fontsize=40, color='cyan', font=FONT_PATH).set_pos(('center', 1700)).set_duration(duration).set_opacity(0.7)
    clips.append(brand)

    # 6. Final Audio Mix
    music = AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.15).set_duration(duration)
    final_audio = CompositeAudioClip([voice, music])

    final = CompositeVideoClip(clips).set_audio(final_audio)
    final.write_videofile(os.path.join("output_videos", data['title'].replace(" ", "_") + ".mp4"), fps=24, preset='ultrafast', threads=4)

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]: render(f)
