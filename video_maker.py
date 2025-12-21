import json, os, subprocess, random, re, math
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM VIDEO MAKER v3.0 - Synced Subtitles & Dynamic Visuals
# ═══════════════════════════════════════════════════════════════════════════════

FONT_NAME = "Montserrat-Bold"

# Voice Pool for variety
VOICE_POOL = [
    "en-US-ChristopherNeural",
    "en-US-GuyNeural",
    "en-US-DavisNeural",
]

# All zodiac images for variety
ALL_ZODIAC_IMAGES = [
    "assets/zodiac_signs/Aries.jpg", "assets/zodiac_signs/Taurus.jpg",
    "assets/zodiac_signs/Gemini.jpg", "assets/zodiac_signs/Cancer.jpg",
    "assets/zodiac_signs/Leo.jpg", "assets/zodiac_signs/Virgo.jpg",
    "assets/zodiac_signs/Libra.jpg", "assets/zodiac_signs/Scorpio.jpg",
    "assets/zodiac_signs/Sagittarius.jpg", "assets/zodiac_signs/Capricorn.jpg",
    "assets/zodiac_signs/Aquarius.jpg", "assets/zodiac_signs/Pisces.jpg"
]

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# ═══════════════════════════════════════════════════════════════════════════════
# TEXT CLEANING - Remove all artifacts
# ═══════════════════════════════════════════════════════════════════════════════

def clean_speech(text):
    """Aggressively clean text for TTS - remove all artifacts."""
    # Remove JSON-like patterns
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    # Remove hashtags, asterisks, colons followed by text
    text = re.sub(r'[#\*]', '', text)
    text = re.sub(r':\s*', '. ', text)  # Replace : with period
    # Remove quotes
    text = re.sub(r'["""\'\'`]', '', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_subtitle(text):
    """Clean text for subtitles - even more aggressive."""
    text = clean_speech(text)
    # Remove any remaining special characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

# ═══════════════════════════════════════════════════════════════════════════════
# VIGNETTE EFFECT
# ═══════════════════════════════════════════════════════════════════════════════

def create_vignette(width, height):
    """Creates a vignette overlay using numpy."""
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    vignette = np.clip((R - 0.6) / 0.8, 0, 1) * 180
    vignette = vignette.astype(np.uint8)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    alpha_channel = Image.fromarray(vignette)
    img.putalpha(alpha_channel)
    path = "temp_vignette.png"
    img.save(path)
    return path

# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC CAMERA MOTION - More dramatic
# ═══════════════════════════════════════════════════════════════════════════════

def apply_camera_motion(clip, duration, motion_type):
    """Apply dramatic camera motion to an image clip."""
    w, h = clip.size
    
    if motion_type == 0:  # Dramatic Zoom In
        def zoom(t):
            progress = t / duration
            return 1 + 0.25 * progress  # 25% zoom
        return clip.resize(zoom).set_duration(duration)
    
    elif motion_type == 1:  # Dramatic Zoom Out
        def zoom(t):
            progress = t / duration
            return 1.25 - 0.25 * progress
        return clip.resize(zoom).set_duration(duration)
    
    elif motion_type == 2:  # Ken Burns Left-to-Right
        def pos(t):
            progress = t / duration
            return (-100 + 200 * progress, 'center')
        return clip.set_position(pos).set_duration(duration)
    
    elif motion_type == 3:  # Ken Burns Top-to-Bottom
        def pos(t):
            progress = t / duration
            return ('center', -100 + 200 * progress)
        return clip.set_position(pos).set_duration(duration)
    
    elif motion_type == 4:  # Zoom + Rotate feeling (zoom with drift)
        def transform(t):
            progress = t / duration
            scale = 1.1 + 0.1 * math.sin(progress * math.pi)
            return scale
        return clip.resize(transform).set_duration(duration)
    
    else:  # Subtle pulse
        def pulse(t):
            return 1.05 + 0.03 * math.sin(t * 2)
        return clip.resize(pulse).set_duration(duration)

# ═══════════════════════════════════════════════════════════════════════════════
# PARSE SRT SUBTITLES
# ═══════════════════════════════════════════════════════════════════════════════

def parse_vtt(vtt_path):
    """Parse VTT subtitle file into list of (start, end, text) tuples."""
    subtitles = []
    if not os.path.exists(vtt_path):
        return subtitles
    
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match VTT time format: 00:00:00.000 --> 00:00:00.000
    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n(.+?)(?=\n\n|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for start_str, end_str, text in matches:
        # Parse time
        def parse_time(t):
            parts = t.split(':')
            h, m = int(parts[0]), int(parts[1])
            s, ms = parts[2].split('.')
            return h * 3600 + m * 60 + int(s) + int(ms) / 1000
        
        start = parse_time(start_str)
        end = parse_time(end_str)
        clean_text = clean_subtitle(text.strip())
        if clean_text:
            subtitles.append((start, end, clean_text))
    
    return subtitles

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)

    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")[:50]
    video_type = data.get('type', 'daily')
    
    print(f"🔱 RENDERING: {safe_title}")

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. GENERATE VOICE WITH SUBTITLES
    # ═══════════════════════════════════════════════════════════════════════════
    txt = clean_speech(data['script_text'])
    voice = random.choice(VOICE_POOL)
    rate = random.choice(["-5%", "-8%", "-10%"])
    
    print(f"   Voice: {voice} | Rate: {rate}")
    
    # Generate voice AND subtitles
    try:
        result = subprocess.run([
            "edge-tts", 
            "--voice", voice, 
            f"--rate={rate}",
            "--text", txt, 
            "--write-media", "v.mp3",
            "--write-subtitles", "v.vtt"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"   ⚠️ TTS Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️ TTS Exception: {e}")
    
    if not os.path.exists("v.mp3") or os.path.getsize("v.mp3") < 1000:
        print("❌ TTS Failed!")
        return False
    
    voice_clip = AudioFileClip("v.mp3")
    duration = voice_clip.duration + 0.5
    
    # Parse synced subtitles
    subtitles = parse_vtt("v.vtt")
    print(f"   📝 Parsed {len(subtitles)} subtitle chunks")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. BACKGROUND MUSIC
    # ═══════════════════════════════════════════════════════════════════════════
    music_files = [m for m in os.listdir("assets/music") if m.endswith(".mp3")]
    if music_files:
        music = AudioFileClip(os.path.join("assets/music", random.choice(music_files)))
        music = music.volumex(0.08).set_duration(duration)
    else:
        music = None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DYNAMIC VISUALS - Multiple images with dramatic motion
    # ═══════════════════════════════════════════════════════════════════════════
    clips = []
    
    # Dark base
    base = ColorClip((1080, 1920), (5, 5, 15), duration=duration)
    clips.append(base)
    
    # Get images - use provided + random extras for variety
    main_imgs = data.get('images', [])
    if not main_imgs:
        main_imgs = [random.choice(ALL_ZODIAC_IMAGES)]
    
    # Add 2-3 random extra images for visual variety
    extra_imgs = random.sample([i for i in ALL_ZODIAC_IMAGES if i not in main_imgs], 
                               min(3, len(ALL_ZODIAC_IMAGES) - len(main_imgs)))
    all_imgs = main_imgs + extra_imgs
    random.shuffle(all_imgs)
    
    # Create 5-6 segments with different images
    num_segments = min(6, len(all_imgs) + 2)
    segment_dur = duration / num_segments
    
    for i in range(num_segments):
        img_path = all_imgs[i % len(all_imgs)]
        if not os.path.exists(img_path):
            continue
            
        img_clip = ImageClip(img_path).resize(height=2200)  # Oversized for motion
        img_clip = img_clip.set_position('center')
        
        # Apply random dramatic motion
        motion_type = random.randint(0, 5)
        img_clip = apply_camera_motion(img_clip, segment_dur, motion_type)
        img_clip = img_clip.set_start(i * segment_dur)
        
        # Crossfade transitions
        if i > 0:
            img_clip = img_clip.crossfadein(0.5)
        
        clips.append(img_clip)
    
    # Add dark overlay for text readability
    overlay = ColorClip((1080, 1920), (0, 0, 0), duration=duration).set_opacity(0.3)
    clips.append(overlay)
    
    # Add vignette
    vignette_path = create_vignette(1080, 1920)
    vignette = ImageClip(vignette_path).set_duration(duration)
    clips.append(vignette)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. SYNCED SUBTITLES
    # ═══════════════════════════════════════════════════════════════════════════
    
    for start, end, text in subtitles:
        sub_duration = end - start
        if sub_duration < 0.1 or not text:
            continue
        
        # Create clean subtitle with high contrast
        try:
            sub_clip = TextClip(
                text.upper(),
                fontsize=80,
                color='white',
                font=FONT_NAME,
                stroke_color='black',
                stroke_width=4,
                method='caption',
                size=(950, None)
            )
            
            sub_clip = sub_clip.set_position(('center', 1100))
            sub_clip = sub_clip.set_start(start).set_duration(sub_duration)
            sub_clip = sub_clip.crossfadein(0.05).crossfadeout(0.05)
            
            clips.append(sub_clip)
        except Exception as e:
            print(f"   ⚠️ Subtitle error: {e}")
            continue
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. FINAL COMPOSITION
    # ═══════════════════════════════════════════════════════════════════════════
    
    final_video = CompositeVideoClip(clips, size=(1080, 1920))
    
    # Audio mix
    audio_clips = [voice_clip]
    if music:
        audio_clips.append(music)
    final_video = final_video.set_audio(CompositeAudioClip(audio_clips))
    
    # Fade out
    final_video = final_video.fadeout(0.3)
    
    # Write output
    output_path = os.path.join("output_videos", f"{safe_title}.mp4")
    final_video.write_videofile(output_path, fps=30, preset='ultrafast', audio_codec='aac')
    
    # Cleanup
    for f in ["v.mp3", "v.vtt", "temp_vignette.png"]:
        if os.path.exists(f): os.remove(f)
    
    print(f"✅ DONE: {output_path}")
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    
    plan_files = [f for f in os.listdir('.') if f.startswith('plan_') and f.endswith('.json')]
    print(f"📂 Found {len(plan_files)} plans")

    for p in plan_files:
        try:
            with open(p, 'r') as f: data = json.load(f)
            
            if not data.get('active', True): 
                print(f"⏭️ SKIP (Inactive): {p}")
                continue
            if data.get('status') == 'done':
                print(f"✅ SKIP (Done): {p}")
                continue

            success = render(p)

            if success:
                data['status'] = 'done'
                with open(p, 'w') as f: json.dump(data, f, indent=4)
                print(f"💾 Marked {p} as DONE")
            
        except Exception as e:
            print(f"❌ Error {p}: {e}")
            import traceback
            traceback.print_exc()
