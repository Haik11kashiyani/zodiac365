import json, os, subprocess, random, re, math, textwrap, sys
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
from datetime import datetime

# Import generator for auto-updates (Ensure path is correct)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from generator_zodiac import generate_content
except ImportError:
    generate_content = None

try:
    import video_sourcer
except ImportError:
    video_sourcer = None

# Import uploader
    print("⚠️ Generator not found. Auto-update disabled.")

# Import uploader
try:
    from youtube_uploader import upload_video
    print("✅ YouTube Uploader imported successfully!")
except ImportError as e:
    upload_video = None
    print(f"⚠️ YouTube Uploader not found. Auto-upload disabled. Error: {e}")
except Exception as e:
    upload_video = None
    print(f"❌ Error importing YouTube Uploader: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════════════════════
# WESTERN VIRAL VIDEO MAKER v5.0
# Fixes: Subtitle Overflow, Random Images, Voice Emotion
# ═══════════════════════════════════════════════════════════════════════════════

FONT_NAME = "Montserrat-Bold"

# Updated for variety and emotion
VOICE_POOL = [
    "en-US-ChristopherNeural", 
    "en-US-GuyNeural", 
    "en-US-DavisNeural",
    "en-US-JennyNeural"
]

# Sign Mapping to Images
ZODIAC_SIGNS = {
    "Aries": "assets/zodiac_signs/Aries.jpg",
    "Taurus": "assets/zodiac_signs/Taurus.jpg",
    "Gemini": "assets/zodiac_signs/Gemini.jpg",
    "Cancer": "assets/zodiac_signs/Cancer.jpg",
    "Leo": "assets/zodiac_signs/Leo.jpg",
    "Virgo": "assets/zodiac_signs/Virgo.jpg",
    "Libra": "assets/zodiac_signs/Libra.jpg",
    "Scorpio": "assets/zodiac_signs/Scorpio.jpg",
    "Sagittarius": "assets/zodiac_signs/Sagittarius.jpg",
    "Capricorn": "assets/zodiac_signs/Capricorn.jpg",
    "Aquarius": "assets/zodiac_signs/Aquarius.jpg",
    "Pisces": "assets/zodiac_signs/Pisces.jpg"
}

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def clean_speech(text):
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'[#\*]', '', text)
    text = re.sub(r':\s*', '. ', text)
    text = re.sub(r'["""\'\'`]', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    # Add filler pause logic handled by SSML, but text is clean here
    return text.strip()

def clean_subtitle(text):
    t = clean_speech(text)
    t = re.sub(r'[^\w\s.,!?-]', '', t)
    return t.strip()

def create_cinematic_overlay(width, height):
    """Creates a professional bottom-shadow gradient for text readability."""
    # Create a gradient mask
    # Top 60% transparent, Bottom 40% fades to black
    
    # We can use a simple ColorClip with opacity, but a gradient is 'Pro'.
    # Since creating a gradient alpha mask in moviepy/numpy manually is verbose,
    # let's stick to a reliable semi-transparent black ColorClip at the bottom for now,
    # or generate a PNG.
    
    # High-End: Solid Black bar with low opacity is "Netflix Style" for subtitles.
    # Gradient is better. Let's create a PNG on the fly using Pillow.
    
    path = "temp_cinematic_overlay.png" # Changed filename to avoid conflict with old vignette
    if os.path.exists(path): return path
    
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Gradient from Y=60% to 100%
    start_y = int(height * 0.6)
    for y in range(start_y, height):
        # Alpha 0 to 220
        alpha = int((y - start_y) / (height - start_y) * 220)
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
    img.save(path)
    return path

def wrap_text_dynamic(text, max_char=20):
    """Wrap text to ensure it fits."""
    return "\n".join(textwrap.wrap(text, width=max_char))

# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL ASSETS GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_particle_overlay(width, height):
    """Create a dust/particle overlay using noise."""
    # Create random noise
    noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
    # Threshold to keep only few "particles"
    particles = np.where(noise > 250, 200, 0).astype(np.uint8)
    # Make RGBA
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    alpha = Image.fromarray(particles)
    img.putalpha(alpha)
    path = "temp_particles.png"
    img.save(path)
    return path

def create_glow_box(width, height, y_start, box_width=900, box_height=150):
    """Create a box for subtitles."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Coordinates
    x1 = (width - box_width) // 2
    y1 = y_start
    x2 = x1 + box_width
    y2 = y1 + box_height
    
    # Rounded Box
    draw.rounded_rectangle([x1, y1, x2, y2], radius=30, fill=(0, 0, 0, 160))
    
    path = "temp_sub_box.png"
    img.save(path)
    return path

def create_vignette(width, height):
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    vignette = np.clip((R - 0.4) / 0.8, 0, 1) * 220
    vignette = vignette.astype(np.uint8)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    alpha = Image.fromarray(vignette)
    img.putalpha(alpha)
    path = "temp_vignette.png"
    img.save(path)
    return path

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIC TO FIND RELEVANT IMAGES
# ═══════════════════════════════════════════════════════════════════════════════

def get_relevant_images(data):
    """
    SMART IMAGE SELECTOR v2.0
    - Analyzes script content for themes (Love, Career, Health, Travel)
    - Tracks usage in image_usage.json to avoid repetition
    - Prioritizes themed images, then least-used general images
    - Guarantees no image repeats within a single video
    """
    title = data.get('title', '')
    target = data.get('target', '')
    script_text = data.get('script_text', '').lower() + " " + title.lower()
    
    # --- 1. DETECT SIGN ---
    detected_sign = None
    for sign in ZODIAC_SIGNS.keys():
        if sign.upper() in title.upper() or sign.upper() in target.upper():
            detected_sign = sign
            break
    
    if not detected_sign:
        print("⚠️ No sign detected, using fallback")
        detected_sign = "Aries"  # Default fallback
    
    # --- 2. DETECT THEME FROM SCRIPT KEYWORDS ---
    THEME_KEYWORDS = {
        "Love": ['love', 'romance', 'partner', 'heart', 'relationship', 'dating', 'marriage', 'soulmate', 'attraction', 'affection'],
        "Career": ['money', 'job', 'work', 'finance', 'career', 'wealth', 'business', 'success', 'promotion', 'income', 'investment'],
        "Health": ['health', 'energy', 'wellness', 'sick', 'healing', 'body', 'mind', 'vitality', 'exercise', 'meditation'],
        "Travel": ['travel', 'trip', 'journey', 'foreign', 'abroad', 'moving', 'adventure', 'vacation', 'explore', 'destination']
    }
    
    detected_theme = None
    for theme, keywords in THEME_KEYWORDS.items():
        if any(kw in script_text for kw in keywords):
            detected_theme = theme
            print(f"🧠 Script Theme Detected: {detected_theme}")
            break
    
    # --- 3. LOAD USAGE TRACKER ---
    tracker_path = os.path.join(os.path.dirname(__file__), "image_usage.json")
    try:
        with open(tracker_path, 'r') as f:
            usage_tracker = json.load(f)
    except:
        usage_tracker = {}
    
    # --- 4. GET ALL AVAILABLE IMAGES FOR THIS SIGN ---
    sign_dir = os.path.join(os.path.dirname(__file__), "assets", "zodiac_signs", detected_sign)
    all_images = []
    
    if os.path.isdir(sign_dir):
        all_images = sorted([
            os.path.join(sign_dir, f) 
            for f in os.listdir(sign_dir) 
            if f.endswith(('.jpg', '.png')) and os.path.getsize(os.path.join(sign_dir, f)) > 5000
        ])
    
    if not all_images:
        print(f"❌ No images found for {detected_sign}, using legacy path")
        legacy_path = f"assets/zodiac_signs/{detected_sign}.jpg"
        if os.path.exists(legacy_path):
            return [legacy_path]
        return [list(ZODIAC_SIGNS.values())[0]]
    
    print(f"📂 Found {len(all_images)} images for {detected_sign}")
    
    # --- 5. PRIORITIZE THEMED IMAGES ---
    themed_images = []
    general_images = []
    
    for img in all_images:
        filename = os.path.basename(img)
        if detected_theme and detected_theme in filename:
            themed_images.append(img)
        else:
            general_images.append(img)
    
    # --- 6. SORT BY USAGE (LEAST USED FIRST) ---
    def get_usage_count(img_path):
        return usage_tracker.get(img_path, 0)
    
    themed_images.sort(key=get_usage_count)
    general_images.sort(key=get_usage_count)
    
    # --- 7. SELECT IMAGES (5 needed for typical video) ---
    selected = []
    num_needed = 5
    
    # First: Pick themed images (if available)
    for img in themed_images:
        if len(selected) >= num_needed:
            break
        if img not in selected:
            selected.append(img)
            print(f"✅ Selected THEMED: {os.path.basename(img)} (used {get_usage_count(img)}x)")
    
    # Then: Fill with least-used general images
    for img in general_images:
        if len(selected) >= num_needed:
            break
        if img not in selected:
            selected.append(img)
            print(f"✅ Selected GENERAL: {os.path.basename(img)} (used {get_usage_count(img)}x)")
    
    # --- 8. UPDATE USAGE TRACKER ---
    for img in selected:
        usage_tracker[img] = usage_tracker.get(img, 0) + 1
    
    try:
        with open(tracker_path, 'w') as f:
            json.dump(usage_tracker, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save usage tracker: {e}")
    
    return selected

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════

def render(data):
    # with open(plan_file, 'r') as f: data = json.load(f) # REMOVED: Data passed directly
    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")[:50]
    print(f"🔱 RENDERING: {safe_title}")

    # 1. VOICE
    txt = clean_speech(data['script_text'])
    voice = random.choice(VOICE_POOL)
    rate = random.choice(["-5%", "-8%"]) # Simple rate
    
    print(f"   Voice: {voice}")
    
    try:
        # FIX: Call via python module to avoid Windows PATH issues with 'edge-tts' exe
        cmd = [
            sys.executable, "-m", "edge_tts",
            "--voice", voice,
            f"--rate={rate}",
            "--text", txt,
            "--write-media", "v.mp3"
        ]
        
        # Windows-specific: Hide console window
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        subprocess.run(cmd, capture_output=True, text=True, timeout=120, startupinfo=startupinfo)
    except Exception as e:
        print(f"   ⚠️ TTS Error: {e}")
        return False
        
    if not os.path.exists("v.mp3") or os.path.getsize("v.mp3") < 1000:
        return False
        
    voice_clip = AudioFileClip("v.mp3")
    total_dur = voice_clip.duration + 1.0 # Renamed for clarity

    # 2. AUDIO MIX
    audio_clips = [voice_clip]
    music_dir = "assets/music"
    music_files = []
    if os.path.exists(music_dir):
        music_files = [m for m in os.listdir(music_dir) if m.endswith(".mp3")]
    
    if music_files:
        music = AudioFileClip(os.path.join(music_dir, random.choice(music_files)))
        music = music.volumex(0.08).set_duration(total_dur) # Slight boost to 0.08
        audio_clips.append(music)
    
    # SFX - Removed as per request (Silent delivery)
    whoosh = None  # Disabled
    
    # 3. VISUALS
    # --- VISUALS ---
    # Try Video Background First (If Pexels Key exists)
    video_bg_paths = []
    
    if os.environ.get("PEXELS_API_KEY") and video_sourcer: 
        target_sign = data.get('target', 'Aries')
        # Request 3 Scenes for a standard short
        video_bg_paths = video_sourcer.get_b_roll_sequence(data.get('script_text', '') + " " + data.get('title', ''), target_sign, count=3)
    
    main_visual_clip = None
    
    if video_bg_paths:
        print(f"🎬 Using Multi-Scene Video Sequence: {len(video_bg_paths)} clips")
        video_clips = []
        
        # Calculate duration per clip to fill total_dur
        # But we want to preserve flow. 
        # Divide total duration equally
        part_dur = total_dur / len(video_bg_paths)
        
        for i, v_path in enumerate(video_bg_paths):
            if not os.path.exists(v_path): continue
            
            clip = VideoFileClip(v_path, audio=False)
            
            # Resize / Crop to filling vertical
            # Assuming vertical source (checked in sourcer), just ensure height 1920
            if clip.h != 1920:
                clip = clip.resize(height=1920)
            if clip.w < 1080:
                # If width is too small after height resize (rare for HD), resize by width
                clip = clip.resize(width=1080)
            
            clip = clip.set_position("center")
            
            # Loop loop if source is too short for its part
            if clip.duration < part_dur:
                 clip = vfx.loop(clip, duration=part_dur + 1.0)
            else:
                 clip = clip.subclip(0, part_dur + 1.0) # Buffer
                 
            clip = clip.set_duration(part_dur)
            clip = clip.set_start(i * part_dur)
            
            # Crossfade
            if i > 0:
                clip = clip.crossfadein(1.0) # 1 second smooth dissolve
            
            video_clips.append(clip)
            
        main_visual_clip = CompositeVideoClip(video_clips, size=(1080, 1920)).set_duration(total_dur)
        
    else:
        # FALLBACK TO IMAGES (Your existing logic)
        images = get_relevant_images(data)
        if not images:
             print("❌ CRITICAL: No visuals found.")
             return None
             
        # Create Image Clips (Ken Burns etc)
        image_clips = []
        base = ColorClip((1080, 1920), (5, 5, 10), duration=total_dur)
        image_clips.append(base)
        
        # Calculate segments
        num_segments = 5
        seg_dur = total_dur / num_segments
        
        for i in range(num_segments):
            img_path = images[i % len(images)]
            if not os.path.exists(img_path): continue
            
            img_clip = ImageClip(img_path).resize(height=2300)
            img_clip = img_clip.set_position('center')
            
            # "ALIVE" Cinematic Motion Logic
            m_type = i % 4
            
            # Base resize to ensure coverage
            # Default height 2300 gives (2300/1920)*1080 approx 1293 width.
            # Screen width 1080. Surplus ~213px. Safe drift +/- 100px.
            
            # 1. SLOW ZOOM OUT (Documentary Style)
            if m_type == 0: 
                # Start zoomed in (1.2) and slowly drift out to 1.0
                # High quality, professional look.
                img_clip = img_clip.resize(height=2300)
                img_clip = img_clip.set_position('center')
                img_clip = img_clip.resize(lambda t: 1.2 - 0.05 * (t / seg_dur))
                
            # 2. CINEMATIC PAN (Safe Linear Move)
            elif m_type == 1:
                img_clip = img_clip.resize(height=2400) # Bigger for more pan room
                # Width approx 1350. Limit +/- 130
                def pan_func(t):
                     # Smooth ease-in-out drift
                     p = (math.sin(t * 0.5) + 1) / 2 # 0 to 1
                     x_offset = -120 + (240 * p) # -120 to +120
                     return ('center', 'center') # MoviePy set_position is tricky with centers in func
                
                # Simple linear that is SAFE
                # X center is 540. We want to move from 440 to 640 (offset -100 to +100)
                # Img width ~1350. Half is 675. 
                # TopLeft X needed for Center X=540 is 540-675 = -135.
                # We want to vary X from -235 to -35.
                
                # Let's use standard 'center' anchor but offset relative to it?
                # Easier: Use fixed resize and compute top-left manually
                img_w = 1080 * (2400/1920) # ~1350
                start_x = (1080 - img_w) / 2 # Center
                
                def pan_safe(t):
                    # Move left to right slowly
                    current_x = start_x - 100 + (20 * t) 
                    return (current_x, 'center')
                img_clip = img_clip.set_position(pan_safe)

            # 3. ORBIT (Circular/Elliptical Drift)
            elif m_type == 2:
                img_clip = img_clip.resize(height=2500)
                # Lots of room.
                img_w = 1080 * (2500/1920) # ~1400
                base_x = (1080 - img_w) / 2
                base_y = (1920 - 2500) / 2
                
                def orbit_func(t):
                    # Small circle movement
                    x_off = 40 * math.cos(t)
                    y_off = 40 * math.sin(t)
                    return (base_x + x_off, base_y + y_off)
                img_clip = img_clip.set_position(orbit_func)

            # 4. DRAMATIC ZOOM (Ken Burns)
            else:
                 img_clip = img_clip.resize(height=2300)
                 img_clip = img_clip.set_position('center')
                 # Start at 1.0, zoom in to 1.15
                 img_clip = img_clip.resize(lambda t: 1.0 + 0.15 * (t / seg_dur))
            
            # Determine strict duration
            img_clip = img_clip.set_start(i * seg_dur).set_duration(seg_dur)
            if i > 0: img_clip = img_clip.crossfadein(0.5) 
            image_clips.append(img_clip)
            
            # Audio Whoosh removed
        main_visual_clip = concatenate_videoclips(image_clips, method="compose")

    # Overlays (applied on top of main_visual_clip)
    overlay_clips = []

    # Particle/Noise
    particle_path = create_particle_overlay(1080, 1920)
    particles = ImageClip(particle_path).set_duration(total_dur).set_opacity(0.15)
    overlay_clips.append(particles)
    
    # Dark Overlay for text
    overlay = ColorClip((1080, 1920), (0,0,0), duration=total_dur).set_opacity(0.3)
    overlay_clips.append(overlay)
    
    # Vignette (old one, if still desired)
    # vignette_path = create_vignette(1080, 1920)
    # vignette = ImageClip(vignette_path).set_duration(total_dur)
    # overlay_clips.append(vignette)
    
    # PREMIUM HEADER OVERLAY ("Viral" Style)
    # 1. Main Title (The Sign or Topic) - BIG & BOLD
    title_text = data.get('target', 'ZODIAC').upper()
    title_clip = TextClip(
        title_text,
        fontsize=75,
        color='white',
        font="Arial-Black", 
        stroke_color='black',
        stroke_width=4, # Thicker stroke
        align='center'
    )
    title_clip = title_clip.set_position(('center', 150))
    # Add shadow for better visibility
    # (Shadow logic can be complex in moviepy, sticking to strong stroke for now)
    
    # 2. Sub Title (The Context) - GOLD & SPACED
    sub_text = "FORECAST"
    if data['type'] == 'daily':
        # FIXED: Check daily type FIRST, then handle date
        date_str = data.get('date', 'TODAY')
        sub_text = f"{date_str} • DAILY"
    elif data['type'] == 'monthly':
        sub_text = "THIS MONTH"
    elif data['type'] == 'yearly':
        sub_text = "2026 PREDICTION"
    elif data['type'] == 'compatibility':
        sub_text = "COMPATIBILITY"
        
    sub_clip = TextClip(
        sub_text,
        fontsize=30, 
        color='#FFD700', # Gold
        font="Arial-Bold",
        kerning=3, 
        align='center'
    )
    # Position sub-title slightly below main title
    sub_clip = sub_clip.set_position(('center', 150 + title_clip.h + 10))
    
    # Add both to overlay_clips
    title_clip = title_clip.set_start(0).set_duration(total_dur)
    sub_clip = sub_clip.set_start(0).set_duration(total_dur)
    overlay_clips.append(title_clip)
    overlay_clips.append(sub_clip)

    # 4. SUBTITLES (Refined: Smaller & Cleaner)
    subtitle_text = clean_subtitle(txt)
    words = subtitle_text.split()
    chunk_size = 5 
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    if chunks:
        chunk_dur = voice_clip.duration / len(chunks)
        # MOVED UP SLIGHTLY
        BOX_Y_START = 1450 
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip(): continue
            start = i * chunk_dur
            
            wrapped = wrap_text_dynamic(chunk.upper(), max_char=24) # More chars allowed per line
            num_lines = wrapped.count('\n') + 1
            
            box_h = 130 if num_lines == 1 else 210
            
            center_y = BOX_Y_START + (box_h // 2)
            
            # IMPROVED SUBTITLE: Yellow text on semi-transparent Black Box
            txt_clip = TextClip(
                wrapped, 
                fontsize=40, 
                color='yellow', 
                font=FONT_NAME,
                stroke_color='black', 
                stroke_width=2, 
                method='caption',
                align='center',
                size=(900, None),
                bg_color='rgba(0,0,0,0.6)' # Semi-transparent black background
            )
            txt_clip = txt_clip.set_position(('center', center_y - (txt_clip.h // 2) - 5)) 
            txt_clip = txt_clip.set_start(start).set_duration(chunk_dur)
            overlay_clips.append(txt_clip)

    # --- ASSEMBLE ---
    # Add Cinematic Overlay (Pro Readability)
    cinematic_overlay_path = create_cinematic_overlay(1080, 1920)
    cinematic_overlay_clip = ImageClip(cinematic_overlay_path).set_duration(total_dur)
    overlay_clips.append(cinematic_overlay_clip)

    # Combine all overlays into a single overlay composite
    all_overlays = CompositeVideoClip(overlay_clips, size=(1080, 1920)).set_duration(total_dur)

    # Final composition: main visual + all overlays
    final_video = CompositeVideoClip([main_visual_clip, all_overlays], size=(1080, 1920))
    final_video = final_video.set_audio(CompositeAudioClip(audio_clips)).set_duration(total_dur)
    final_video = final_video.fadeout(0.5)
    
    # PATH FIX: Use absolute path for output to avoid CWD issues
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "output_videos")
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    
    output_file = os.path.join(out_dir, f"{safe_title}.mp4")
    # OPTIMIZATION: threads=4, fps=24    
    final_video.write_videofile(
        output_file, 
        fps=30, 
        codec='libx264', 
        audio_codec='aac',
        threads=4, 
        preset='medium'
    )
    
    # Cleanup
    for f in ["v.mp3", "temp_vignette.png", "temp_sub_box.png", "temp_particles.png", "temp_box_1.png", "temp_box_2.png"]:
        if os.path.exists(f): os.remove(f)
    return output_file


def check_freshness_and_update(data):
    """Check if data is stale and regenerate if needed."""
    if not generate_content: return False, data
    
    # Defaults
    now = datetime.now()
    is_stale = False
    mode = data.get('type', 'daily')
    target = data.get('target', 'Aries')
    current_date_str = data.get('date', '')
    
    target = data.get('target', 'Aries')
    current_date_str = data.get('date', '')
    
    # 0. Empty Content Check (Force Regenerate if text missing)
    if not data.get('script_text'):
        print(f"⚠️ Missing script text for {target}. Marking as STALE.")
        is_stale = True
    
    # 1. Daily Check
    elif mode == 'daily':
        # Expected format: "Jan 05" (or "Jan 5")
        # Let's check against today's formatted date
        today_str = now.strftime("%b %d") # e.g. Dec 28
        
        # SMART DATE CHECK: Allow Future Dates (Pre-generation)
        is_stale = False
        if current_date_str == "TODAY":
            pass # Always fresh if explicitly marked TODAY (dynamic)
        elif current_date_str != today_str:
            # If mismatch, check if it's strictly in the PAST
            try:
                # Parse "Jan 13" with current year
                # strptime defaults to 1900, so we need to add year logic if verifying strictly
                # Simple Hack: compare string equality first (done above).
                # If distinct, assume stale UNLESS it looks like future?
                
                # Robust Parse
                dt_cur = datetime.strptime(f"{current_date_str} {now.year}", "%b %d %Y")
                dt_today = datetime.strptime(f"{today_str} {now.year}", "%b %d %Y")
                
                if dt_cur < dt_today:
                     print(f"🔄 STALE (Past) CONTENT DETECTED: {target} (Date: {current_date_str})")
                     is_stale = True
                else:
                     print(f"📅 FUTURE CONTENT DETECTED: {target} (Date: {current_date_str}). Keeping.")
                     is_stale = False
            except:
                # If parse fails (formatting issue), default to strict equality check (STALE)
                print(f"⚠️ Date Parse Failed for '{current_date_str}'. resetting.")
                is_stale = True
            
    # 2. Monthly Check
    elif mode == 'monthly':
        cur_month = now.strftime("%B") # December
        # If "December" not in title or text, might be old?
        # Better: use a stored 'month' field if we had one, otherwise simplistic check
        # Assuming we don't store separate month field yet, skipping unless explicit
        pass
        
    # Regenerate if stale
    if is_stale:
        print(f"♻️  Auto-Generating new content for {target}...")
        try:
            today_str = now.strftime("%b %d")
            new_data = generate_content(mode, target, today_str)
            if new_data:
                # Merge new data into old object to keep other fields (like images?)
                # Actually, generator returns full valid object with images.
                # We should update keys.
                data.update(new_data)
                # Reset status to ensure render
                data['status'] = 'pending'
                print("✅ Content Updated Successfully!")
                return True, data
        except Exception as e:
            print(f"❌ Generation Failed: {e}")
            
    return False, data

if __name__ == "__main__":
    # Ensure robust pathing regardless of CWD
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output_videos')
    
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    plan_files = []
    if os.path.exists(EXAMPLES_DIR):
        plan_files.extend([os.path.join(EXAMPLES_DIR, f) for f in os.listdir(EXAMPLES_DIR) if f.startswith('plan_') and f.endswith('.json')])
    
    # Also check current directory for backward compatibility
    plan_files.extend([os.path.abspath(f) for f in os.listdir('.') if f.startswith('plan_') and f.endswith('.json')])
    
    for path in plan_files:
        if not os.path.exists(path): continue
        
        try:
            with open(path, 'r', encoding='utf-8') as f: 
                content = json.load(f)
            
            # Normalize to list to support BATCH processing
            if isinstance(content, list):
                plans = content
            else:
                plans = [content]
            
            any_processed = False
            file_updated = False
            
            for i, data in enumerate(plans):
                if not data.get('active', True): continue
                
                # AUTO-UPDATE CHECK
                updated, new_data = check_freshness_and_update(data)
                if updated:
                    plans[i] = new_data
                    data = new_data  # CRITICAL FIX: Update local reference too!
                    file_updated = True
                    # If updated, it comes back as 'pending', so it will fall through to render below
                
                if data.get('status') == 'done': 
                    # Check if already rendered but NOT uploaded - retry upload
                    if upload_video and not data.get('uploaded', False):
                        # Try to find the output video file
                        safe_title = re.sub(r'[\\/*?:"<>|]', "", data.get('title', 'Unknown')).replace(" ", "_")[:50]
                        output_file = os.path.join(OUTPUT_DIR, f"{safe_title}.mp4")
                        if os.path.exists(output_file):
                            print(f"🔄 Retrying upload for: {data.get('title', 'Unknown')}")
                            if upload_video(output_file, data):
                                data['uploaded'] = True
                                file_updated = True
                                print("🚀 Video Uploaded & Marked as Completed.")
                            else:
                                print("⚠️ Upload retry failed.")
                    continue
                
                
                print(f"Processing: {data.get('title', 'Unknown')}")
                video_path = render(data)
                if video_path: 
                    data['status'] = 'done'
                    any_processed = True
                    file_updated = True
                    
                    # UPLOAD LOGIC
                    print(f"📤 Attempting upload... (upload_video available: {upload_video is not None})")
                    if upload_video and not data.get('uploaded', False):
                        if upload_video(video_path, data):
                            data['uploaded'] = True
                            print("🚀 Video Uploaded & Marked as Completed.")
                        else:
                            print("⚠️ Upload skipped or failed.")
            
            # Save back updated statuses AND content
            if file_updated:
                with open(path, 'w', encoding='utf-8') as f: 
                    if isinstance(content, list):
                        json.dump(plans, f, indent=4)
                    else:
                        json.dump(plans[0], f, indent=4)
                        
        except Exception as e: 
            print(f"Error processing {path}: {e}")
