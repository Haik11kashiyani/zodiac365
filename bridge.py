import os
import json
import subprocess
import sys
import re
import random
import datetime

# Import existing logic
from generator_zodiac import generate_zodiac_video
from moviepy.editor import AudioFileClip
from video_sourcer import get_b_roll_sequence
try:
    from youtube_uploader import upload_video
except ImportError:
    upload_video = None
def clean_speech(text):
    """Cleans text for TTS to prevent truncation/errors."""
    # Remove emojis
    text = re.sub(r'[^\w\s.,!?-]', '', text) 
    # Remove brackets
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    # Remove markdown/hashtags
    text = re.sub(r'[#\*]', '', text)
    # Standardize spacing
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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
                    text = re.sub(r'<[^>]+>', '', text)
                    
                    words = text.split()
                    # Chunking logic
                    chunk_size = 10 # More words per screen (User Request: "place same amount of text")
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
    
    chunk_size = 10 # More words per screen for fallback too
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

def convert_to_image_sequence(input_path, output_dir_name):
    """
    Converts video to a JPEG sequence. Returns AssetSpec object or None.
    This bypasses browser video decoding entirely, solving CI timeouts.
    """
    try:
        # Check if ffmpeg exists
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        asset_root = "video-engine/public/assets"
        seq_dir = os.path.join(asset_root, output_dir_name)
        os.makedirs(seq_dir, exist_ok=True)
        
        log_info(f"🎞️ Converting {os.path.basename(input_path)} to Image Sequence in {output_dir_name}...")
        
        # Output pattern: frame_0000.jpg
        output_pattern = os.path.join(seq_dir, "frame_%04d.jpg")
        
        cmd = [
            "ffmpeg", 
            "-i", input_path,
            "-start_number", "0",  # Start at frame_0000 to match JS 0-index
            "-r", "30",            # Force 30fps to match composition
            "-vf", "scale=-2:720", # 720p height
            "-q:v", "5",           # Quality 5 (good balance)
            "-y",
            output_pattern
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Count frames
        frames = [f for f in os.listdir(seq_dir) if f.endswith('.jpg')]
        count = len(frames)
        log_success(f"   Generated {count} frames.")
        
        return {
            "type": "sequence",
            "prefix": f"/assets/{output_dir_name}/",
            "count": count
        }
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log_warning(f"⚠️ Sequence conversion failed: {e}. Falling back to video.")
        return None


def process_plan(filename):
    """Runs the full pipeline (Audio -> Build -> Upload) for a single plan file."""
    log_section(f"Processing: {filename}")
    
    with open(filename, 'r') as f:
        data = json.load(f)
        
    target = data.get('target', 'Unknown')
    safe_target = target.replace(' ', '_').replace('/', '-')
    script_text = data.get('script_text', '')
    
    if not script_text:
        log_error(f"Skipping {filename}: No script text.")
        return

    # 2. GENERATE AUDIO & SUBTITLES (EdgeTTS)
    log_info("Generating Audio & VTT...")
    audio_file = os.path.abspath(f"video-engine/public/{safe_target}.mp3")
    vtt_file = os.path.abspath(f"video-engine/public/{safe_target}.vtt")
    
    os.makedirs(os.path.dirname(audio_file), exist_ok=True)
    
    voice = "en-US-ChristopherNeural"
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", clean_speech(script_text), 
        "--write-media", audio_file,
        "--write-subtitles", vtt_file
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        log_error(f"EdgeTTS failed for {filename}: {e}")
        return
    
    # 2.5 CALCULATE DURATION
    video_duration_frames = 1800 # Default 60s
    try:
        if os.path.exists(audio_file):
            with AudioFileClip(audio_file) as audio:
                # User Request: "after the sentenc is speken... then after 0.5 sec complit the video"
                duration_sec = audio.duration + 0.5
                video_duration_frames = int(duration_sec * 30)
                log_info(f"calculated duration: {duration_sec}s ({video_duration_frames} frames)")
    except Exception as e:
        log_error(f"Could not calculate audio duration: {e}")
    
    # 3. PARSE VTT
    captions = []
    try:
        if os.path.exists(vtt_file):
            captions = parse_vtt(vtt_file)
    except Exception: pass
    
    if not captions:
        log_warning("No captions parsed from VTT. Using fallback generator.")
        captions = generate_fallback_captions(script_text)
        
    log_success(f"Final caption count: {len(captions)}")
        
    # 4. GET VISUALS
    log_info("Sourcing Visuals...")
    video_paths = []
    if os.environ.get("PEXELS_API_KEY"):
         requested_count = 6
         video_paths = get_b_roll_sequence(script_text, target, count=requested_count)
         if len(video_paths) < (requested_count / 2):
             log_warning("Switching to ANIMATION MODE (Low video count).")
             video_paths = [] 
         else:
             log_success(f"Found {len(video_paths)} relevant videos. Using Video Mode.")

    remotion_assets = []
    asset_dir = "video-engine/public/assets"
    os.makedirs(asset_dir, exist_ok=True)
    
    import shutil
    for i, vp in enumerate(video_paths):
        if os.path.exists(vp):
            ext = os.path.splitext(vp)[1]
            dest_name = f"clip_{i}{ext}"
            dest_path = os.path.join(asset_dir, dest_name)
            seq_asset = convert_to_image_sequence(vp, f"clip_{i}")
            if seq_asset:
                remotion_assets.append(seq_asset)
            else:
                shutil.copy(vp, dest_path)
                remotion_assets.append(f"/assets/{dest_name}")
            
    if not remotion_assets:
        remotion_assets = ["https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg"]
        log_warning("No Pexels videos downloaded. Using fallback image.")

    # 5. WRITE INPUT.JSON
    input_data = {
        "scriptText": script_text,
        "audioSrc": f"/{safe_target}.mp3",
        "captions": captions,
        "images": remotion_assets,
        "title": data.get('youtube_title', 'Zodiac Video'),
        "durationInFrames": video_duration_frames,
        "optimizeForCI": os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
    }
    
    input_path = "video-engine/input.json"
    with open(input_path, "w") as f:
        json.dump(input_data, f, indent=2)
    log_success(f"Data written to {input_path}")

    # 6. BUILD VIDEO
    log_info("Building Video...")
    video_engine_dir = os.path.join(os.path.dirname(__file__), "video-engine")
    try:
        subprocess.run(["npm", "run", "build"], cwd=video_engine_dir, check=True, shell=True)
        log_success("Build Complete!")
    except subprocess.CalledProcessError:
        log_error("Build Failed. Skipping upload.")
        return

    # 7. UPLOAD
    output_video_path = os.path.join(video_engine_dir, "out", "video.mp4")
    if os.path.exists(output_video_path) and upload_video:
        log_info("Uploading...")
        if upload_video(output_video_path, data):
             # Mark as done in file
             data['status'] = 'uploaded'
             with open(filename, 'w') as f:
                 json.dump(data, f, indent=2)
             log_success(f"Done: {filename}")
        else:
            log_error(f"Upload failed for {filename}.")
    else:
        log_warning("Upload skipped (File missing or Uploader disabled).")

import argparse
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", action="store_true", help="Process all pending plan_*.json files")
    args = parser.parse_args()

    if args.batch:
        log_section("🔥 BATCH MODE ACTIVATED")
        plans = glob.glob("plan_*.json")
        pending = []
        for p in plans:
            try:
                with open(p, 'r') as f:
                    d = json.load(f)
                    if d.get('status') != 'uploaded':
                        pending.append(p)
            except Exception as e:
                log_error(f"Error reading plan file {p}: {e}")
        
        log_info(f"Found {len(pending)} pending plans.")
        if not pending:
            log_info("No pending plans found. Exiting batch mode.")
            return

        for p in pending:
            process_plan(p)
    else:
        # Legacy single mode (env var driven)
        target = os.environ.get('TARGET_SIGN', 'Aries')
        mode = os.environ.get('VIDEO_MODE', 'daily')
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        
        log_section(f"Single Mode: {target} ({mode})")
        # 1. GENERATE CONTENT (Python)
        success = generate_zodiac_video(mode, target, date_str)
        if success:
             safe_target = target.replace(' ', '_').replace('/', '-')
             filename = f"plan_{mode}_{safe_target}.json"
             process_plan(filename)
        else:
            log_error("Content generation failed.")
            sys.exit(1)


if __name__ == "__main__":
    main()
