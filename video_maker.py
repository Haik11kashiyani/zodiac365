import json
import os
import sys
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx # Crucial for audio looping
from gtts import gTTS

# --- CONFIGURATION ---
ASSETS_DIR = "assets/tarot_cards"
OUTPUT_DIR = "output_videos"
FONT_PATH = "assets/fonts/Cinzel-Bold.ttf"
MUSIC_PATH = "assets/music/mystical_bg.mp3"

# --- CLOUD FIX: IMAGEMAGICK DETECTION ---
if os.name == 'posix':
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def create_video_from_plan(plan_file):
    print(f"🎬 Processing: {plan_file}")
    
    # 1. LOAD PLAN
    with open(plan_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. GENERATE VOICE (TTS)
    print("🎙️ Generating Voiceover...")
    tts = gTTS(text=data['script_text'], lang='en', tld='com', slow=False)
    voice_path = "temp_voice.mp3"
    tts.save(voice_path)
    
    voice_clip = AudioFileClip(voice_path)
    total_duration = voice_clip.duration + 2 # Add buffer
    print(f"⏱️ Video Duration: {total_duration:.2f} seconds")

    # 3. BACKGROUND MUSIC LAYER
    if os.path.exists(MUSIC_PATH):
        print("🎵 Adding Background Music...")
        bg_music = AudioFileClip(MUSIC_PATH)
        
        # Loop music if it's shorter than video
        if bg_music.duration < total_duration:
            bg_music = afx.audio_loop(bg_music, duration=total_duration)
        else:
            bg_music = bg_music.subclip(0, total_duration)
            
        # Lower volume to 15% so voice is clear
        bg_music = bg_music.volumex(0.15)
        
        # Mix Voice + Music
        final_audio = CompositeAudioClip([voice_clip, bg_music])
    else:
        print("⚠️ No music found. Using voice only.")
        final_audio = voice_clip

    # 4. VISUALS (Cards & Background)
    bg_clip = ColorClip(size=(1080, 1920), color=(15, 5, 25), duration=total_duration) # Deep mystical purple
    
    card_files = data['card_images']
    card_clips = []
    time_per_card = total_duration / len(card_files)
    
    for i, card_filename in enumerate(card_files):
        img_path = os.path.join(ASSETS_DIR, card_filename)
        
        if not os.path.exists(img_path):
            print(f"⚠️ Asset missing {img_path}. Skipping.")
            continue

        # Resize and Position
        img = ImageClip(img_path).resize(width=950).set_position("center")
        img = img.set_start(i * time_per_card).set_duration(time_per_card)
        img = img.crossfadein(0.5) # Smooth transition
        card_clips.append(img)

    # 5. TEXT OVERLAY (Title)
    # Check if custom font exists, otherwise use system default
    # Note: On Linux, we need absolute path for custom fonts sometimes
    if os.path.exists(FONT_PATH):
        font_use = os.path.abspath(FONT_PATH)
    else:
        font_use = 'DejaVu-Sans-Bold' # Linux fallback

    try:
        print(f"✍️ Drawing Title using {os.path.basename(font_use)}...")
        txt_clip = TextClip(
            data['title'], 
            fontsize=55, 
            color='#FFD700', # Gold color
            font=font_use,
            size=(900, None), 
            method='caption'
        ).set_position(('center', 250)).set_duration(total_duration)
    except Exception as e:
        print(f"⚠️ Text Rendering Error: {e}")
        txt_clip = None

    # 6. COMPOSITE & RENDER
    layers = [bg_clip] + card_clips
    if txt_clip: layers.append(txt_clip)
    
    final_video = CompositeVideoClip(layers).set_audio(final_audio)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    output_filename = os.path.join(OUTPUT_DIR, data['file_name'])
    
    # Render fast ('ultrafast') for testing
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac', 
        preset='ultrafast',
        threads=4
    )
    
    # Cleanup
    if os.path.exists(voice_path): os.remove(voice_path)
    
    print("✅ Video Render Complete!")
    return output_filename

if __name__ == "__main__":
    # Auto-find newest plan
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot') and f.endswith('.json')]
    if files:
        latest = max(files, key=os.path.getctime)
        create_video_from_plan(latest)
    else:
        print("❌ No plan file found. Run generator_tarot.py first.")
        sys.exit(1)
