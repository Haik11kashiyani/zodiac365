import json
import os
import sys
import subprocess
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx
from PIL import Image
import numpy as np

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS

if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

ASSETS = "assets/tarot_cards"
OUTPUT = "output_videos"
FONT = "assets/fonts/Cinzel-Bold.ttf"
MUSIC = "assets/music/mystical_bg.mp3"

def generate_voice(text, filename):
    print("🎙️ Generating Human Voice...")
    cmd = ["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", text, "--write-media", filename]
    try:
        subprocess.run(cmd, check=True)
        return True
    except: return False

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
    print(f"📼 Rendering Cinematic: {data['file_name']}...")
    
    cards = []
    for c in data['card_images']:
        path = os.path.join(ASSETS, c)
        if os.path.exists(path): cards.append(path)
    if not cards: sys.exit(1)

    if not generate_voice(data['script_text'], "voice.mp3"): sys.exit(1)
    voice = AudioFileClip("voice.mp3")
    duration = voice.duration + 2
    
    audio = voice
    if os.path.exists(MUSIC):
        try:
            bg = AudioFileClip(MUSIC)
            bg = afx.audio_loop(bg, duration=duration).volumex(0.2)
            audio = CompositeAudioClip([voice, bg])
        except: pass

    bg_clip = ColorClip((1080, 1920), (5, 5, 10), duration=duration)
    clips = [bg_clip]
    
    intro = 3.0
    time_per_card = (duration - intro) / len(cards)
    
    for i, path in enumerate(cards):
        img = ImageClip(path).resize(width=1080).set_pos("center")
        img = img.set_start(intro + i*time_per_card).set_duration(time_per_card).crossfadein(0.5)
        clips.append(zoom(img))

    font_use = FONT if os.path.exists(FONT) else 'DejaVu-Sans-Bold'
    
    def text_gen(txt, size, col, y, start, dur):
        stroke = TextClip(txt.upper(), fontsize=size+2, color='black', font=font_use, size=(950, None), method='caption').set_pos(('center', y+4))
        main = TextClip(txt.upper(), fontsize=size, color=col, font=font_use, size=(950, None), method='caption').set_pos(('center', y))
        return CompositeVideoClip([stroke, main]).set_start(start).set_duration(dur).crossfadein(0.5)

    try:
        # Title
        clips.append(text_gen(data['title'], 70, '#FFD700', 300, 0, 3.5))
        
        # Dynamic Overlays
        overlays = data.get('overlays', [])
        for ol in overlays:
            txt = ol.get('text', '')
            tm = ol.get('time', 'middle')
            
            if tm == 'start': start, dur = 0.5, 3
            elif tm == 'end': continue 
            else: start, dur = duration/2, 4
            
            clips.append(text_gen(txt, 60, 'white', 1400, start, dur))
        
        # UPDATED VISUAL CTA: Website Address
        # Show "THEZODIACVAULT.KESUG.COM" for last 5 seconds
        clips.append(text_gen("thezodiacvault.kesug.com", 50, '#00FFFF', 1500, duration-5, 5))
            
    except Exception as e: print(f"Text Error: {e}")

    final = CompositeVideoClip(clips).set_audio(audio)
    if not os.path.exists(OUTPUT): os.makedirs(OUTPUT)
    final.write_videofile(os.path.join(OUTPUT, data['file_name']), fps=24, preset='ultrafast', threads=4)
    if os.path.exists("voice.mp3"): os.remove("voice.mp3")

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot')]
    if files: render(max(files, key=os.path.getctime))
