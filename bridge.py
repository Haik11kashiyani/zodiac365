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
    """Parses a WebVTT file cleanly, handling edge cases."""
    captions = []
    
    if not os.path.exists(vtt_file):
        log_error(f"VTT file not found: {vtt_file}")
        return []
        
    with open(vtt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Regex to handle various VTT timestamps:
    # 00:00:00.000 or 00:00.000 (mm:ss.ms)
    # Separator can be --> or ->
    # Decimals can be . or ,
    time_pattern = re.compile(r'((?:\d{2}:)?\d{2}:\d{2}[.,]\d{3})\s*-->\s*((?:\d{2}:)?\d{2}:\d{2}[.,]\d{3})')
    
    def parse_time(t_str):
        t_str = t_str.replace(',', '.')
        parts = t_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return 0.0

    current_start = None
    current_end = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        match = time_pattern.search(line)
        if match:
            current_start = parse_time(match.group(1))
            current_end = parse_time(match.group(2))
            
            # Look ahead for text
            if i + 1 < len(lines):
                text = lines[i+1].strip()
                # If next line is empty, maybe text is on i+2 (skip blank lines)
                if not text and i + 2 < len(lines):
                     text = lines[i+2].strip()

                if text and 'WEBVTT' not in text:
                    # Clean tags like <v Voice> or <b>
                    text = re.sub(r'<[^>]+>', '', text)
                    
                    words = text.split()
                    # Chunking logic
                    chunk_size = 2
                    chunks = [' '.join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
                    
                    duration = current_end - current_start
                    if len(chunks) > 0:
                        chunk_duration = duration / len(chunks)
                        for k, chunk in enumerate(chunks):
                            c_start = current_start + (k * chunk_duration)
                            c_end = c_start + chunk_duration
                            captions.append({
                                "start": c_start,
                                "end": c_end,
                                "text": chunk.upper()
                            })
                            
    return captions

def generate_fallback_captions(script_text, duration_est=60):
    """Generates estimated captions if VTT parsing fails."""
    log_info("Generating fallback captions...")
    words = script_text.split()
    total_words = len(words)
    time_per_word = duration_est / max(total_words, 1)
    
    captions = []
    current_time = 0.0
    
    chunk_size = 2
    for i in range(0, total_words, chunk_size):
        chunk = words[i:i+chunk_size]
        text = " ".join(chunk).upper()
        duration = len(chunk) * time_per_word
        
        captions.append({
            "start": current_time,
            "end": current_time + duration,
            "text": text
        })
        current_time += duration
        
    return captions

from cli_utils import log_section, log_info, log_success, log_error

# ... (imports) ...

def main():
    target = os.environ.get('TARGET_SIGN', 'Aries')
    mode = os.environ.get('VIDEO_MODE', 'daily')
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    log_section(f"Starting Bridge for {target} ({mode})")
    
    # 1. GENERATE CONTENT (Python)
    success = generate_zodiac_video(mode, target, date_str)
    if not success:
        log_error("Content generation failed.")
        sys.exit(1)
        
    # Find the file
    safe_target = target.replace(' ', '_').replace('/', '-')
    filename = f"plan_{mode}_{safe_target}.json"
    
    with open(filename, 'r') as f:
        data = json.load(f)
        
    # 2. GENERATE AUDIO & SUBTITLES (EdgeTTS)
    log_section("Generating Audio & VTT")
    script_text = data.get('script_text', '')
    if not script_text:
        log_error("No script text found.")
        sys.exit(1)
        
    audio_file = os.path.abspath(f"video-engine/public/{safe_target}.mp3")
    vtt_file = os.path.abspath(f"video-engine/public/{safe_target}.vtt")
    
    os.makedirs(os.path.dirname(audio_file), exist_ok=True)
    
    voice = "en-US-ChristopherNeural"
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", script_text,
        "--write-media", audio_file,
        "--write-subtitles", vtt_file
    ]
    subprocess.run(cmd, check=True)
    
    # 3. PARSE VTT FOR REMOTION
    # Try parsing VTT
    captions = []
    try:
        if os.path.exists(vtt_file):
            captions = parse_vtt(vtt_file)
    except Exception as e:
        log_error(f"VTT parsing failed: {e}")
        
    # FALLBACK: If parsing failed or no captions found, generate from script
    if not captions:
        log_warning("No captions parsed from VTT. Using fallback generator.")
        captions = generate_fallback_captions(script_text)
        
    log_success(f"Final caption count: {len(captions)}")
    
    # 4. GET VISUALS
    log_section("Sourcing Visuals")
    video_paths = []
    if os.environ.get("PEXELS_API_KEY"):
         video_paths = get_b_roll_sequence(script_text, target, count=6)
    
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
            remotion_assets.append(f"/assets/{dest_name}")
            
    if not remotion_assets:
        remotion_assets = ["https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg"]
        
    # 5. WRITE INPUT.JSON
    input_data = {
        "scriptText": script_text,
        "audioSrc": f"/{safe_target}.mp3",
        "captions": captions,
        "images": remotion_assets,
        "title": data.get('youtube_title', 'Zodiac Video')
    }
    
    input_path = "video-engine/input.json"
    with open(input_path, "w") as f:
        json.dump(input_data, f, indent=2)
        
    log_success(f"Bridge Complete. Data written to {input_path}")
    log_info("Now run: cd video-engine && npm run build")

if __name__ == "__main__":
    main()
