import json
import os
import sys
from moviepy.config import change_settings
from moviepy.editor import *
from gtts import gTTS

# --- CONFIGURATION ---
ASSETS_DIR = "assets/tarot_cards"
OUTPUT_DIR = "output_videos"

# --- CLOUD FIX: IMAGEMAGICK DETECTION ---
# GitHub Actions runs on Linux (posix). We must explicitly tell MoviePy where ImageMagick is.
if os.name == 'posix':
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def create_video_from_plan(plan_file):
    print(f"🎬 Processing: {plan_file}")
    
    # 1. LOAD PLAN
    with open(plan_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. GENERATE AUDIO (Voiceover)
    print("🎙️ Generating Voiceover...")
    tts = gTTS(text=data['script_text'], lang='en', tld='com', slow=False)
    audio_path = "temp_voice.mp3"
    tts.save(audio_path)
    
    # Load audio to determine video length
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration + 2 # Add 2 seconds buffer for smooth ending
    print(f"⏱️ Video Duration: {total_duration:.2f} seconds")

    # 3. CREATE BACKGROUND
    # Dark mystical purple background
    bg_clip = ColorClip(size=(1080, 1920), color=(20, 10, 40), duration=total_duration)
    
    # 4. CREATE VISUALS (The Cards)
    card_files = data['card_images']
    card_clips = []
    
    # Calculate screen time per card
    # If 3 cards, each gets 33% of the time.
    time_per_card = total_duration / len(card_files)
    
    print("🎴 Stacking Card Visuals...")
    for i, card_filename in enumerate(card_files):
        img_path = os.path.join(ASSETS_DIR, card_filename)
        
        # Safety Check: Does image exist?
        if not os.path.exists(img_path):
            print(f"⚠️ WARNING: Asset missing {img_path}. Skipping.")
            continue

        # Create Image Clip
        # Resize to 900px width (fits well on 1080px screen)
        img = ImageClip(img_path).resize(width=900).set_position("center")
        
        # Timing: Start at i * time, last for 'time_per_card'
        img = img.set_start(i * time_per_card).set_duration(time_per_card)
        
        # Effect: Smooth Fade In
        img = img.crossfadein(0.5)
        
        card_clips.append(img)

    # 5. CREATE TEXT (The Title)
    # Using 'DejaVu-Sans-Bold' because it is standard on Linux/GitHub Servers.
    # 'Arial' often crashes Linux scripts because it is Windows-only.
    try:
        print("✍️ Drawing Text Overlay...")
        txt_clip = TextClip(
            data['title'], 
            fontsize=60, 
            color='white', 
            font='DejaVu-Sans-Bold', # Linux safe font
            size=(900, None), 
            method='caption'
        ).set_position(('center', 200)).set_duration(total_duration)
    except Exception as e:
        print(f"⚠️ Text Rendering Failed (ImageMagick Policy?): {e}")
        txt_clip = None

    # 6. COMPOSITE (Mix Layers)
    layers = [bg_clip] + card_clips
    if txt_clip:
        layers.append(txt_clip)
        
    final_video = CompositeVideoClip(layers)
    final_video = final_video.set_audio(audio_clip)

    # 7. RENDER OUTPUT
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    output_filename = os.path.join(OUTPUT_DIR, data['file_name'])
    print(f"⚙️ Rendering file: {output_filename}")
    
    # preset='ultrafast' is CRITICAL for GitHub Actions to save minutes.
    # threads=4 uses all CPU cores available on the runner.
    final_video.write_videofile(
        output_filename, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac', 
        preset='ultrafast',
        threads=4
    )
    
    # Cleanup temp audio
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    print("✅ Video Render Complete!")
    return output_filename

if __name__ == "__main__":
    # AUTOMATION LOGIC:
    # Scan the folder for the newest 'plan_tarot_*.json' file and render it.
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot') and f.endswith('.json')]
    
    if files:
        # Sort by creation time (newest first)
        latest_file = max(files, key=os.path.getctime)
        create_video_from_plan(latest_file)
    else:
        print("❌ No plan file found. Please run generator_tarot.py first.")
        sys.exit(1)