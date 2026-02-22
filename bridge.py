import os
import json
import subprocess
import sys
import re
import random
import time
import datetime
import shutil

# Import existing logic
from generator_zodiac import generate_zodiac_video
from moviepy.editor import AudioFileClip
from video_sourcer import get_b_roll_sequence
from cli_utils import log_info, log_warning, log_error, log_success, log_section
import signal

def run_command_with_timeout(cmd, cwd, timeout_sec):
    """
    Runs a command with a timeout and ensures the ENTIRE process tree is killed if it times out.
    This prevents orphaned Node.js processes from piling up in CI.
    """
    if os.name == 'nt':
        # Windows: Use Popen with shell=True. taskkill /T will handle the tree.
        p = subprocess.Popen(cmd, cwd=cwd, shell=True)
    else:
        # Unix: Use process groups so we can kill the whole group
        p = subprocess.Popen(cmd, cwd=cwd, shell=True, preexec_fn=os.setsid)
        
    try:
        p.wait(timeout=timeout_sec)
        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, cmd)
    except subprocess.TimeoutExpired:
        log_error(f"Command timed out after {timeout_sec}s. Killing process tree...")
        if os.name == 'nt':
            subprocess.run(f"taskkill /F /T /PID {p.pid}", shell=True)
        else:
             # Kill the process group (negate pid)
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            except:
                p.kill()
        raise

try:
    from youtube_uploader import upload_video
    log_info("✅ youtube_uploader imported successfully.")
except ImportError as e:
    upload_video = None
    log_warning(f"⚠️ Could not import youtube_uploader: {e}")
import imageio_ffmpeg
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

def split_sentences(text):
    """Splits text into sentences, keeping punctuation."""
    # Split by . ! ? followed by space or end of string
    # We use a capture group to keep the delimiter
    parts = re.split(r'([.!?]+)', text)
    sentences = []
    current = ""
    for p in parts:
        if re.match(r'^[.!?]+$', p):
            current += p
            sentences.append(current.strip())
            current = ""
        else:
            current += p
    if current.strip():
        sentences.append(current.strip())
    return [s for s in sentences if s]

def get_audio_duration(fpath):
    """Gets audio duration using MoviePy (more reliable than system ffprobe)."""
    try:
        with AudioFileClip(fpath) as clip:
            return clip.duration
    except Exception as e:
        log_error(f"Duration check failed for {fpath}: {e}")
        return 0.0

def write_vtt(captions, path):
    """Writes a list of caption dicts to a VTT file."""
    def fmt_time(s):
        ms = int((s % 1) * 1000)
        m, s_int = divmod(int(s), 60)
        h, m = divmod(m, 60)
        return f"{h:02}:{m:02}:{s_int:02}.{ms:03}"

    with open(path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for c in captions:
            start = fmt_time(c['start'])
            end = fmt_time(c['end'])
            text = c['text']
            # Escape newlines in text just in case? No, VTT allows newlines.
            f.write(f"{start} --> {end}\n{text}\n\n")

def generate_segmented_audio(script_text, audio_out, vtt_out):
    """
    Generates audio sentence-by-sentence with 0.2s pauses.
    Stitches audio and realigns VTT timestamps.
    """
    import shutil
    
    sentences = split_sentences(script_text)
    if not sentences:
        log_error("No sentences found.")
        return False
        
    temp_dir = os.path.join("video-engine", "public", ".temp_tts_" + str(random.randint(1000,9999)))
    os.makedirs(temp_dir, exist_ok=True)
    
    segments = []
    voice = "en-US-ChristopherNeural"
    
    log_info(f"Generating audio for {len(sentences)} sentences...")
    
    for i, sent in enumerate(sentences):
        safe_sent = clean_speech(sent)
        if not safe_sent: continue
        
        seg_audio = os.path.join(temp_dir, f"seg_{i}.mp3")
        seg_vtt = os.path.join(temp_dir, f"seg_{i}.vtt")
        
        # Small delay to be safe
        if i > 0: time.sleep(0.15)
        
        cmd = [
            sys.executable, "-m", "edge_tts",
            "--voice", voice,
            "--text", safe_sent,
            "--write-media", seg_audio,
            "--write-subtitles", seg_vtt
        ]
        try:
            subprocess.run(cmd, check=True, timeout=120)
            segments.append({
                "audio": seg_audio,
                "vtt": seg_vtt,
            })
        except subprocess.CalledProcessError as e:
            log_error(f"Failed segment {i}: {e}")
            # Retry
            try:
                # Retry without punctuation
                cleaned = re.sub(r'[^\w\s]', '', safe_sent)
                cmd = [
                    sys.executable, "-m", "edge_tts",
                    "--voice", voice,
                    "--text", cleaned,
                    "--write-media", seg_audio,
                    "--write-subtitles", seg_vtt
                ]
                subprocess.run(cmd, check=True, timeout=120)
                segments.append({
                    "audio": seg_audio,
                    "vtt": seg_vtt,
                })
            except Exception as e2:
                 log_error(f"Retry failed for segment {i}: {e2}")

    if not segments:
        return False

    # Generate Silence
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    silence_file = os.path.join(temp_dir, "silence.mp3")
    subprocess.run([
        ffmpeg_exe, "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", 
        "-t", "0.2", "-q:a", "2", "-acodec", "libmp3lame", "-y", silence_file
    ], check=True)
    
    # Create Concat List
    concat_txt = os.path.join(temp_dir, "concat.txt")
    with open(concat_txt, 'w') as f:
        for i, seg in enumerate(segments):
            p = os.path.abspath(seg['audio']).replace('\\', '/')
            s = os.path.abspath(silence_file).replace('\\', '/')
            f.write(f"file '{p}'\n")
            if i < len(segments) - 1:
                f.write(f"file '{s}'\n")
            
    # Stitch Audio
    try:
        subprocess.run([
            ffmpeg_exe, "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, 
            "-c", "copy", "-y", audio_out
        ], check=True)
    except Exception as e:
        log_error(f"Audio stitching failed: {e}")
        return False
        
    # Stitch VTT
    final_captions = []
    current_offset = 0.0
    silence_duration = 0.2
    
    for i, seg in enumerate(segments):
        seg_captions = parse_vtt(seg['vtt'])
        dur = get_audio_duration(seg['audio'])
        
        if dur == 0.0 and seg_captions:
            dur = seg_captions[-1]['end']
            
        for cap in seg_captions:
            cap['start'] += current_offset
            cap['end'] += current_offset
            final_captions.append(cap)
            
        current_offset += dur 
        if i < len(segments) - 1:
            current_offset += silence_duration
        
    write_vtt(final_captions, vtt_out)
    
    try: shutil.rmtree(temp_dir)
    except: pass
    
    return True

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
            "-vf", "scale=-2:480", # 480p height — smaller files load faster in Remotion
            "-q:v", "8",           # Quality 8 — faster I/O, still acceptable scaled to 1080p
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


def _cleanup_previous_build():
    """Remove leftover assets from previous video build to prevent stale data."""
    asset_dir = "video-engine/public/assets"
    if os.path.exists(asset_dir):
        try:
            shutil.rmtree(asset_dir)
            log_info("🧹 Cleaned previous build assets.")
        except Exception as e:
            log_warning(f"Could not clean assets: {e}")
    # Clean leftover audio/vtt in public/
    public_dir = "video-engine/public"
    if os.path.exists(public_dir):
        for f in os.listdir(public_dir):
            if f.endswith(('.mp3', '.vtt')):
                try:
                    os.remove(os.path.join(public_dir, f))
                except:
                    pass
    # Clean Remotion bundle cache to prevent stale cached bundles
    # from interfering with root component loading
    cache_dirs = [
        "video-engine/node_modules/.cache",
        "video-engine/.remotion",
    ]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                log_info(f"🧹 Cleaned cache: {cache_dir}")
            except Exception as e:
                log_warning(f"Could not clean cache {cache_dir}: {e}")

def _mark_plan_failed(filename, data, reason):
    """Marks a plan as errored so it doesn't retry forever."""
    try:
        data['status'] = 'error'
        data['error_reason'] = reason
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

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
        _mark_plan_failed(filename, data, 'No script text')
        return

    # 1.5 CLEANUP previous build assets
    _cleanup_previous_build()

    # 2. GENERATE AUDIO & SUBTITLES (Segmented for Pauses)
    log_info("Generating Audio & VTT with pauses...")
    audio_file = os.path.abspath(f"video-engine/public/{safe_target}.mp3")
    vtt_file = os.path.abspath(f"video-engine/public/{safe_target}.vtt")
    
    os.makedirs(os.path.dirname(audio_file), exist_ok=True)
    
    success = generate_segmented_audio(script_text, audio_file, vtt_file)
    if not success:
        log_error("Segmented Audio Generation Failed.")
        _mark_plan_failed(filename, data, 'Audio generation failed')
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
    except Exception as e:
        log_error(f"VTT parsing failed: {e}")
    
    if not captions:
        log_warning("No captions parsed from VTT. Using fallback generator.")
        captions = generate_fallback_captions(script_text)
    
    # Ensure all captions are uppercase for style
    for c in captions:
        c['text'] = c['text'].upper()
        
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
        remotion_assets = ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="]
        log_warning("No Pexels videos downloaded. Using inline fallback.")

    # 5. WRITE INPUT.JSON
    input_data = {
        "scriptText": script_text,
        "audioSrc": f"/{safe_target}.mp3",
        "captions": captions,
        "images": remotion_assets,
        "luckyNumbers": data.get('lucky_numbers', []),
        "luckyColor": data.get('lucky_color', ''),
        "monthlyVibe": data.get('monthly_vibe', ''),
        "date": data.get('date', ''),
        "predictionType": data.get('type', 'daily').upper(),
        "title": data.get('youtube_title', 'Zodiac Video'),
        "durationInFrames": video_duration_frames,
        "optimizeForCI": os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
    }
    
    input_path = "video-engine/input.json"
    with open(input_path, "w") as f:
        json.dump(input_data, f, indent=2)
    log_success(f"Data written to {input_path}")

    # 6. BUILD VIDEO (with 20-minute timeout to prevent stuck renders)
    log_info("Building Video...")
    video_engine_dir = os.path.join(os.path.dirname(__file__), "video-engine")
    BUILD_TIMEOUT_SECONDS = 20 * 60  # 20 minutes max per video
    try:
        cmd = "npm run build"
        log_info(f"Executing: {cmd} (timeout: {BUILD_TIMEOUT_SECONDS}s)")
        # Use new helper to ensure process tree cleanup
        run_command_with_timeout(cmd, cwd=video_engine_dir, timeout_sec=BUILD_TIMEOUT_SECONDS)
        log_success("Build Complete!")
    except subprocess.TimeoutExpired:
        log_error(f"Build TIMED OUT after {BUILD_TIMEOUT_SECONDS}s. Skipping this video.")
        _mark_plan_failed(filename, data, f'Build timed out after {BUILD_TIMEOUT_SECONDS}s')
        return
    except subprocess.CalledProcessError as e:
        log_error(f"Build Failed (exit code {e.returncode}). Skipping upload.")
        _mark_plan_failed(filename, data, f'Build failed with exit code {e.returncode}')
        return

    # 7. UPLOAD
    output_video_path = os.path.join(video_engine_dir, "out", "video.mp4")
    
    if not os.path.exists(output_video_path):
        log_error(f"Upload skipped: Video file not found at {output_video_path}")
        return

    # SAVE LOCAL COPY FOR DEBUGGING
    debug_dir = "output_videos"
    os.makedirs(debug_dir, exist_ok=True)
    debug_path = os.path.join(debug_dir, f"{safe_target}.mp4")
    try:
        shutil.copy(output_video_path, debug_path)
        log_success(f"Video saved locally to {debug_path}")
    except Exception as e:
        log_warning(f"Could not save local copy: {e}")


    if not upload_video:
        log_warning("Upload skipped: upload_video function is not available (ImportError previously).")
        return

    log_info("Uploading...")
    if upload_video(output_video_path, data):
         # Mark as done in file
         data['status'] = 'uploaded'
         with open(filename, 'w') as f:
             json.dump(data, f, indent=2)
         log_success(f"Done: {filename}")
    else:
        log_error(f"Upload failed for {filename}.")

import argparse
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", action="store_true", help="Process all pending plan_*.json files")
    args = parser.parse_args()

    if args.batch:
        log_section("🔥 BATCH MODE ACTIVATED")
        MAX_VIDEOS_PER_RUN = 6  # Cap to fit within GitHub Actions 4-hour limit
        plans = glob.glob("plan_*.json")
        pending = []
        for p in plans:
            try:
                with open(p, 'r') as f:
                    d = json.load(f)
                    if d.get('status') not in ('uploaded', 'error'):
                        pending.append(p)
            except Exception as e:
                log_error(f"Error reading plan file {p}: {e}")
        
        # Priority sort: daily first, then monthly, then weekly, then others
        def plan_priority(name):
            if 'daily' in name: return 0
            if 'monthly' in name: return 1
            if 'yearly' in name: return 2
            if 'weekly' in name: return 3
            return 4
        pending.sort(key=plan_priority)
        
        log_info(f"Found {len(pending)} pending plans.")
        if len(pending) > MAX_VIDEOS_PER_RUN:
            log_warning(f"Capping to {MAX_VIDEOS_PER_RUN} videos this run (had {len(pending)} pending). Remaining will process next run.")
            pending = pending[:MAX_VIDEOS_PER_RUN]
        
        if not pending:
            log_info("No pending plans found. Exiting batch mode.")
            return

        success_count = 0
        fail_count = 0
        for idx, p in enumerate(pending):
            try:
                log_info(f"📦 Processing plan {idx+1}/{len(pending)}: {p}")
                process_plan(p)
                # Check if it was actually uploaded
                with open(p, 'r') as f:
                    if json.load(f).get('status') == 'uploaded':
                        success_count += 1
                    else:
                        fail_count += 1
            except Exception as e:
                log_error(f"CRITICAL FAILURE processing {p}: {e}")
                fail_count += 1
                continue
        
        log_section("📊 BATCH SUMMARY")
        log_info(f"Total: {len(pending)} | ✅ Uploaded: {success_count} | ❌ Failed: {fail_count}")
        
        # FATAL ERROR if nothing worked (ensures CI fails)
        if success_count == 0 and fail_count > 0:
            log_error("FATAL: All video builds failed! Exiting with error.")
            sys.exit(1)
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
