import os
import json
import subprocess
import sys
import re
import random
import datetime

# Import existing logic
from generator_zodiac import generate_zodiac_video
from video_sourcer import get_b_roll_sequence

def parse_vtt(vtt_file):
    """Parses a WebVTT file into a JSON list for Remotion."""
    captions = []
    
    with open(vtt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Simple parser for "00:00:00.000 --> 00:00:02.000"
    # EdgeTTS VTT format is usually:
    # WEBVTT
    # 
    # 00:00:00.100 --> 00:00:01.500
    # Hello world
    
    current_start = None
    current_end = None
    
    time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})')
    
    # SPLIT LOGIC: For viral videos, we want 1-3 words max per screen.
    # We will interpolate the time linearly for the words in the line.
    
    for i, line in enumerate(lines):
        line = line.strip()
        match = time_pattern.match(line)
        if match:
            # Parse start/end
            h, m, s, ms = map(int, match.groups()[0:4])
            start_sec = h*3600 + m*60 + s + ms/1000.0
            
            h, m, s, ms = map(int, match.groups()[4:8])
            end_sec = h*3600 + m*60 + s + ms/1000.0
            
            if i + 1 < len(lines):
                text = lines[i+1].strip()
                if text:
                    words = text.split()
                    # Group into chunks of 2-3 words
                    chunk_size = 2 # Aggressive pacing
                    chunks = [' '.join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
                    
                    duration = end_sec - start_sec
                    chunk_duration = duration / len(chunks)
                    
                    for k, chunk in enumerate(chunks):
                        c_start = start_sec + (k * chunk_duration)
                        c_end = c_start + chunk_duration
                        captions.append({
                            "start": c_start,
                            "end": c_end,
                            "text": chunk.upper() # FORCE UPPERCASE
                        })
                    
    return captions

def main():
    target = os.environ.get('TARGET_SIGN', 'Aries')
    mode = os.environ.get('VIDEO_MODE', 'daily')
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    print(f"🚀 Starting Bridge for {target} ({mode})...")
    
    # 1. GENERATE CONTENT (Python)
    # This creates/updates the plan_*.json file
    success = generate_zodiac_video(mode, target, date_str)
    if not success:
        print("❌ Content generation failed.")
        sys.exit(1)
        
    # Find the file
    safe_target = target.replace(' ', '_').replace('/', '-')
    filename = f"plan_{mode}_{safe_target}.json"
    
    with open(filename, 'r') as f:
        data = json.load(f)
        
    # 2. GENERATE AUDIO & SUBTITLES (EdgeTTS)
    print("🎙️ Generating Audio & VTT...")
    script_text = data.get('script_text', '')
    if not script_text:
        print("❌ No script text found.")
        sys.exit(1)
        
    audio_file = os.path.abspath(f"video-engine/public/{safe_target}.mp3")
    vtt_file = os.path.abspath(f"video-engine/public/{safe_target}.vtt")
    
    # Ensure public dir exists
    os.makedirs(os.path.dirname(audio_file), exist_ok=True)
    
    # Run EdgeTTS
    voice = "en-US-ChristopherNeural" # Deep male voice
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", script_text,
        "--write-media", audio_file,
        "--write-vtt", vtt_file
    ]
    subprocess.run(cmd, check=True)
    
    # 3. PARSE VTT FOR REMOTION
    captions = parse_vtt(vtt_file)
    print(f"📝 Parsed {len(captions)} caption segments.")
    
    # 4. GET VISUALS
    # Use existing video_sourcer but just get paths
    print("🎬 Sourcing Visuals...")
    # Remotion needs public URLs or local paths in 'public' folder
    # For now, let's use the local paths provided by sourcer and COPY them to video-engine/public/assets
    
    # Mocking sourcer for now if API missing, else using it
    # We need to make sure sourcer returns list of paths
    video_paths = []
    if os.environ.get("PEXELS_API_KEY"):
         # We need to import the sourcer logic more directly or assume it works
         # sourcer.get_b_roll_sequence returns local paths in assets/videos
         video_paths = get_b_roll_sequence(script_text, target, count=6)
    
    # Copy assets to Remotion public
    remotion_assets = []
    asset_dir = "video-engine/public/assets"
    os.makedirs(asset_dir, exist_ok=True)
    
    import shutil
    for i, vp in enumerate(video_paths):
        if os.path.exists(vp):
            ext = os.path.splitext(vp)[1]
            dest_name = f"clip_{i}{ext}"
            dest_path = os.path.join(asset_dir, dest_name)
            shutil.copy(vp, dest_path)
            # Web path
            remotion_assets.append(f"/assets/{dest_name}")
            
    # Fallback if no video
    if not remotion_assets:
        remotion_assets = ["https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg"]
        
    # 5. WRITE INPUT.JSON
    input_data = {
        "scriptText": script_text,
        "audioSrc": f"/{safe_target}.mp3", # Public relative path
        "captions": captions,
        "images": remotion_assets,
        "title": data.get('youtube_title', 'Zodiac Video')
    }
    
    input_path = "video-engine/input.json"
    with open(input_path, "w") as f:
        json.dump(input_data, f, indent=2)
        
    print(f"✅ Bridge Complete. Data written to {input_path}")
    print("👉 Now run: cd video-engine && npm run build")

if __name__ == "__main__":
    main()
