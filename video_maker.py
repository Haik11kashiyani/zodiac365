import json
import os
import sys
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx
from gtts import gTTS
from PIL import Image
import numpy as np

# --- CRITICAL FIX FOR PILLOW 10.0.0+ ---
# MoviePy uses 'ANTIALIAS' which was removed. We restore it here.
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS
# ---------------------------------------

if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

ASSETS = "assets/tarot_cards"
OUTPUT = "output_videos"
FONT = "assets/fonts/Cinzel-Bold.ttf"
MUSIC = "assets/music/mystical_bg.mp3"

def zoom(clip):
    def effect(get_frame, t):
        img = clip.get_frame(t)
        h, w = img.shape[:2]
        scale = 1 + 0.04 * t
        new_w, new_h = int(w/scale), int(h/scale)
        x, y = (w-new_w)//2, (h-new_h)//2
        pil = Image.fromarray(img).crop((x, y, x+new_w, y+new_h)).resize((w, h), Image.LANCZOS)
        return np.array(pil)
    return clip.fl(effect)

def render(plan):
    with open(plan, 'r') as f: data = json.load(f)
    print(f"📼 Rendering {data['file_name']}...")
    
    # 1. Assets Check
    cards = []
    for c in data['card_images']:
        path = os.path.join(ASSETS, c)
        if os.path.exists(path): cards.append(path)
        else: print(f"❌ Missing: {path}")
    
    if not cards:
        print("❌ FATAL: No cards found.")
        sys.exit(1)

    # 2. Audio (Protected)
    tts = gTTS(data['script_text'], lang='en', tld='com')
    tts.save("voice.mp3")
    voice = AudioFileClip("voice.mp3")
    duration = voice.duration + 2
    
    audio = voice
    if os.path.exists(MUSIC):
        try:
            print("🎵 Loading Background Music...")
            bg = AudioFileClip(MUSIC)
            bg = afx.audio_loop(bg, duration=duration).volumex(0.15)
            audio = CompositeAudioClip([voice, bg])
            print("✅ Music mixed successfully.")
        except:
            print("⚠️ Music failed. Skipping.")
    
    # 3. Visuals
    bg_clip = ColorClip((1080, 1920), (15,5,25), duration=duration)
    clips = [bg_clip]
    
    intro = 3.0
    time_per_card = (duration - intro) / len(cards)
    
    for i, path in enumerate(cards):
        img = ImageClip(path).resize(width=950).set_pos("center")
        img = img.set_start(intro + i*time_per_card).set_duration(time_per_card).crossfadein(0.5)
        clips.append(zoom(img))

    # 4. Text
    font_use = FONT if os.path.exists(FONT) else 'DejaVu-Sans-Bold'
    try:
        title = TextClip(data['title'].upper(), fontsize=60, color='#FFD700', font=font_use, size=(900, None), method='caption')
        title = title.set_pos(('center', 400)).set_duration(3).crossfadeout(0.5)
        clips.append(title)
        
        cta = TextClip("Claim This Energy 👇", fontsize=50, color='white', font=font_use, size=(900, None), method='caption')
        cta = cta.set_pos(('center', 1500)).set_start(duration-4).set_duration(4).crossfadein(1)
        clips.append(cta)
    except: pass

    final = CompositeVideoClip(clips).set_audio(audio)
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    
    final.write_videofile(os.path.join(OUTPUT, data['file_name']), fps=24, preset='ultrafast', threads=4)
    if os.path.exists("voice.mp3"): os.remove("voice.mp3")

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot')]
    if files: render(max(files, key=os.path.getctime))
