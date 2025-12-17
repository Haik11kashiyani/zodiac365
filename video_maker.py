import json
import os
import sys
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx
from gtts import gTTS
from PIL import Image
import numpy as np

ASSETS_DIR = "assets/tarot_cards"
OUTPUT_DIR = "output_videos"
FONT_PATH = "assets/fonts/Cinzel-Bold.ttf"
MUSIC_PATH = "assets/music/mystical_bg.mp3"

if os.name == 'posix':
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = clip.get_frame(t)
        h, w = img.shape[:2]
        scale = 1 + zoom_ratio * t
        new_w, new_h = int(w / scale), int(h / scale)
        x_center, y_center = w // 2, h // 2
        x1 = x_center - new_w // 2
        y1 = y_center - new_h // 2
        pil_img = Image.fromarray(img)
        pil_img = pil_img.crop((x1, y1, x1 + new_w, y1 + new_h))
        pil_img = pil_img.resize((w, h), Image.LANCZOS)
        return np.array(pil_img)
    return clip.fl(effect)

def create_video_from_plan(plan_file):
    print(f"🎬 Processing Premium Video: {plan_file}")
    with open(plan_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. AUDIO
    print("🎙️ Generating Voiceover...")
    tts = gTTS(text=data['script_text'], lang='en', tld='com', slow=False)
    voice_path = "temp_voice.mp3"
    tts.save(voice_path)
    voice_clip = AudioFileClip(voice_path)
    total_duration = voice_clip.duration + 2 
    
    if os.path.exists(MUSIC_PATH):
        bg_music = AudioFileClip(MUSIC_PATH)
        if bg_music.duration < total_duration:
            bg_music = afx.audio_loop(bg_music, duration=total_duration)
        else:
            bg_music = bg_music.subclip(0, total_duration)
        bg_music = bg_music.volumex(0.15)
        final_audio = CompositeAudioClip([voice_clip, bg_music])
    else:
        final_audio = voice_clip

    # 2. VISUALS
    bg_clip = ColorClip(size=(1080, 1920), color=(15, 5, 25), duration=total_duration)
    card_files = data['card_images']
    card_clips = []
    
    intro_duration = 3.0
    time_per_card = (total_duration - intro_duration) / len(card_files)
    
    for i, card_filename in enumerate(card_files):
        img_path = os.path.join(ASSETS_DIR, card_filename)
        if not os.path.exists(img_path): continue

        start_time = intro_duration + (i * time_per_card)
        img = ImageClip(img_path).resize(width=950).set_position("center")
        img = img.set_start(start_time).set_duration(time_per_card).crossfadein(0.5)
        img = zoom_in_effect(img, zoom_ratio=0.04)
        card_clips.append(img)

    # 3. TEXT
    font_use = os.path.abspath(FONT_PATH) if os.path.exists(FONT_PATH) else 'DejaVu-Sans-Bold'

    try:
        title_clip = TextClip(
            data['title'].upper(), fontsize=65, color='#FFD700', font=font_use,
            size=(900, None), method='caption'
        ).set_position(('center', 400)).set_start(0).set_duration(3).crossfadeout(0.5)
    except: title_clip = None

    try:
        cta_clip = TextClip(
            "Claim This Energy 👇", fontsize=50, color='white', font=font_use,
            size=(900, None), method='caption'
        ).set_position(('center', 1500)).set_start(total_duration - 4).set_duration(4).crossfadein(1)
    except: cta_clip = None

    layers = [bg_clip] + card_clips
    if title_clip: layers.append(title_clip)
    if cta_clip: layers.append(cta_clip)
    
    final_video = CompositeVideoClip(layers).set_audio(final_audio)
    
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    output_filename = os.path.join(OUTPUT_DIR, data['file_name'])
    
    final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4)
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
