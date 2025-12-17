import json
import os
import sys
import math
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx
from gtts import gTTS

# --- CONFIGURATION ---
ASSETS_DIR = "assets/tarot_cards"
OUTPUT_DIR = "output_videos"
FONT_PATH = "assets/fonts/Cinzel-Bold.ttf"
MUSIC_PATH = "assets/music/mystical_bg.mp3"

# --- CLOUD FIX ---
if os.name == 'posix':
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def zoom_in_effect(clip, zoom_ratio=0.04):
    """Adds a slow zoom-in effect to images (Ken Burns effect)"""
    def effect(get_frame, t):
        img = clip.get_frame(t)
        h, w = img.shape[:2]
        scale = 1 + zoom_ratio * t
        new_w, new_h = int(w / scale), int(h / scale)
        x_center, y_center = w // 2, h // 2
        x1 = x_center - new_w // 2
        y1 = y_center - new_h // 2
        
        # Crop center to zoom
        import numpy as np
        from PIL import Image
        pil_img = Image.fromarray(img)
        pil_img = pil_img.crop((x1, y1, x1 + new_w, y1 + new_h))
        pil_img = pil_img.resize((w, h), Image.LANCZOS)
        return np.array(pil_img)

    return clip.fl(effect)

def create_video_from_plan(plan_file):
    print(f"🎬 Processing Premium Video: {plan_file}")
    
    # 1. LOAD PLAN
    with open(plan_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. VOICE & AUDIO
    print("🎙️ Generating Voiceover...")
    tts = gTTS(text=data['script_text'], lang='en', tld='com', slow=False)
    voice_path = "temp_voice.mp3"
    tts.save(voice_path)
    
    voice_clip = AudioFileClip(voice_path)
    total_duration = voice_clip.duration + 2
    
    # Background Music
    if os.path.exists(MUSIC_PATH):
        bg_music = AudioFileClip(MUSIC_PATH)
        if bg_music.duration < total_duration:
            bg_music = afx.audio_loop(bg_music, duration=total_duration)
        else:
            bg_music = bg_music.subclip(0, total_duration)
        
        bg_music = bg_music.volumex(0.15) # Low volume
        final_audio = CompositeAudioClip([voice_clip, bg_music])
    else:
        final_audio = voice_clip

    # 3. DYNAMIC VISUALS
    # We want a dark animated background, but a color clip works for now.
    bg_clip = ColorClip(size=(1080, 1920), color=(10, 5, 20), duration=total_duration)
    
    card_files = data['card_images']
    card_clips = []
    
    # Timing Strategy:
    # 0-3s: Intro (Title)
    # 3s - End: Cards Cycle
    intro_duration = 3.0
    remaining_time = total_duration - intro_duration
    time_per_card = remaining_time / len(card_files)
    
    for i, card_filename in enumerate(card_files):
        img_path = os.path.join(ASSETS_DIR, card_filename)
        
        if not os.path.exists(img_path):
            continue

        # Create Image
        start_time = intro_duration + (i * time_per_card)
        
        img = ImageClip(img_path).resize(width=950).set_position("center")
        img = img.set_start(start_time).set_duration(time_per_card)
        img = img.crossfadein(0.5) # Smooth fade
        
        # Add Slide Up Animation (Manual 'set_position')
        # We simulate a "Pop Up" by starting slightly lower
        # (This is hard in basic MoviePy, so we stick to Fade + Zoom for reliability)
        
        card_clips.append(img)

    # 4. TEXT OVERLAYS (The "Viral" Part)
    
    # A. MAIN TITLE (Only for first 3 seconds)
    if os.path.exists(FONT_PATH):
        font_use = os.path.abspath(FONT_PATH)
    else:
        font_use = 'DejaVu-Sans-Bold'

    title_clip = TextClip(
        data['title'].upper(), # Make it UPPERCASE for impact
        fontsize=70, 
        color='#FFD700', # Gold
        font=font_use,
        size=(900, None), 
        method='caption'
    ).set_position(('center', 400)).set_start(0).set_duration(3).crossfadeout(0.5)

    # B. "LISTEN CLOSELY" (Call to action at the end)
    cta_clip = TextClip(
        "Claim This Energy 👇", 
        fontsize=50, 
        color='white', 
        font=font_use,
        size=(900, None),
        method='caption'
    ).set_position(('center', 1500)).set_start(total_duration - 4).set_duration(4).crossfadein(1)

    # 5. ASSEMBLE
    layers = [bg_clip] + card_clips + [title_clip, cta_clip]
    
    final_video = CompositeVideoClip(layers).set_audio(final_audio)
    
    # 6. RENDER
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    output_filename = os.path.join(OUTPUT_DIR, data['file_name'])
    
    # 'ultrafast' for testing, 'medium' for production quality
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac', 
        preset='ultrafast',
        threads=4
    )
    
    if os.path.exists(voice_path): os.remove(voice_path)
    return output_filename

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot') and f.endswith('.json')]
    if files:
        latest = max(files, key=os.path.getctime)
        create_video_from_plan(latest)
    else:
        print("❌ No plan file found.")
        sys.exit(1)
