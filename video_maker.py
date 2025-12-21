import json, os, subprocess, random, re, math
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image, ImageDraw

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM VIDEO MAKER v2.0 - Viral-Ready YouTube Shorts
# ═══════════════════════════════════════════════════════════════════════════════

# Font Configuration
FONT_NAME = "Montserrat-Bold"  # Premium subtitle font
TITLE_FONT = "Cinzel-Bold"     # Title font

# Voice Pool for variety
VOICE_POOL = [
    "en-US-ChristopherNeural",  # Deep, authoritative
    "en-US-GuyNeural",          # Warm, friendly
    "en-US-DavisNeural",        # Calm, mystical
]

# Color Palettes by video type
COLOR_THEMES = {
    "daily": {"overlay": (75, 0, 130, 40), "accent": "#FFD700"},      # Purple + Gold
    "monthly": {"overlay": (0, 77, 77, 40), "accent": "#00CED1"},     # Teal + Cyan
    "yearly": {"overlay": (139, 69, 19, 40), "accent": "#FFD700"},    # Bronze + Gold
    "compatibility": {"overlay": (128, 0, 32, 40), "accent": "#FF69B4"}, # Burgundy + Pink
    "birthday": {"overlay": (255, 105, 180, 30), "accent": "#FFFFFF"}, # Pink + White
    "special": {"overlay": (25, 25, 112, 40), "accent": "#E6E6FA"},   # Midnight + Lavender
}

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def clean_speech(text):
    """Strips hashtags and AI artifacts for clean speech."""
    return re.sub(r'[#\*]', '', text).strip()

def add_ssml_emotion(text):
    """Adds SSML tags for emotional, human-like speech."""
    # Add pauses after sentences
    text = re.sub(r'([.!?])\s+', r'\1<break time="400ms"/> ', text)
    # Add emphasis to key words (randomly select some capitalized words)
    words = text.split()
    for i, word in enumerate(words):
        if word.isupper() and len(word) > 2 and random.random() > 0.5:
            words[i] = f'<emphasis level="strong">{word}</emphasis>'
    return ' '.join(words)

def create_vignette(width, height):
    """Creates a vignette overlay image using fast numpy operations."""
    import numpy as np
    
    # Create coordinate grids
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # Calculate radial distance from center
    R = np.sqrt(X**2 + Y**2)
    
    # Create vignette effect (dark at edges)
    # Start darkening from radius 0.7, full dark at 1.4
    vignette = np.clip((R - 0.7) / 0.7, 0, 1) * 150
    vignette = vignette.astype(np.uint8)
    
    # Create RGBA image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    alpha_channel = Image.fromarray(vignette)
    img.putalpha(alpha_channel)
    
    vignette_path = "temp_vignette.png"
    img.save(vignette_path)
    return vignette_path

def apply_camera_motion(clip, duration, index):
    """Enhanced camera motion with more variety."""
    motion_type = index % 5
    
    if motion_type == 0:  # Zoom In
        return clip.resize(lambda t: 1 + 0.15 * (t/duration)).set_duration(duration)
    elif motion_type == 1:  # Zoom Out
        return clip.resize(lambda t: 1.15 - 0.15 * (t/duration)).set_duration(duration)
    elif motion_type == 2:  # Pan Left to Right
        def pos(t):
            progress = t / duration
            return (-50 + progress * 100, 'center')
        return clip.set_position(pos).set_duration(duration)
    elif motion_type == 3:  # Pan Right to Left
        def pos(t):
            progress = t / duration
            return (50 - progress * 100, 'center')
        return clip.set_position(pos).set_duration(duration)
    else:  # Subtle zoom with hold
        return clip.resize(lambda t: 1.05 + 0.05 * math.sin(t * 0.5)).set_duration(duration)

def create_animated_subtitle(text, start_time, duration, accent_color, width=1000):
    """Creates premium animated subtitle with glow effect."""
    text = text.upper().strip()
    
    # Simple but effective subtitle with stroke
    main_text = TextClip(
        text, fontsize=85, color=accent_color, font=FONT_NAME,
        stroke_color='black', stroke_width=4, method='caption', size=(width, None)
    )
    
    # Position and timing
    main_text = main_text.set_position(('center', 1150))
    main_text = main_text.set_start(start_time).set_duration(duration)
    main_text = main_text.crossfadein(0.1).crossfadeout(0.1)
    
    return main_text

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    with open("config.json", "r") as f: config = json.load(f)

    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")
    video_type = data.get('type', 'daily')
    theme = COLOR_THEMES.get(video_type, COLOR_THEMES['daily'])
    
    print(f"🔱 PREMIUM RENDERING: {safe_title}")
    print(f"   Theme: {video_type} | Accent: {theme['accent']}")

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. EMOTIONAL VOICE GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    txt = clean_speech(data['script_text'])
    
    # Select random voice for variety
    voice = random.choice(VOICE_POOL)
    rate = random.choice(["-5%", "-8%", "-10%"])
    
    print(f"   Voice: {voice} | Rate: {rate}")
    
    # Generate with edge-tts (use = syntax to avoid shell issues with negative values)
    try:
        result = subprocess.run([
            "edge-tts", 
            "--voice", voice, 
            f"--rate={rate}",
            "--text", txt, 
            "--write-media", "v.mp3"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"   ⚠️ TTS Error: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️ TTS Exception: {e}")
    
    if not os.path.exists("v.mp3") or os.path.getsize("v.mp3") < 1000:
        print("❌ TTS Failed!")
        return False
    
    voice_clip = AudioFileClip("v.mp3")
    duration = voice_clip.duration + 1.5  # Extra time for outro
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. BACKGROUND MUSIC (Lower volume for voice prominence)
    # ═══════════════════════════════════════════════════════════════════════════
    music_files = [m for m in os.listdir("assets/music") if m.endswith(".mp3")]
    if music_files:
        music_track = random.choice(music_files)
        music = AudioFileClip(os.path.join("assets/music", music_track))
        music = music.volumex(0.08).set_duration(duration)  # Lower volume
    else:
        music = None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. VISUAL COMPOSITION
    # ═══════════════════════════════════════════════════════════════════════════
    clips = []
    
    # Base dark background
    base = ColorClip((1080, 1920), (8, 8, 20), duration=duration)
    clips.append(base)
    
    # Main images with camera motion
    imgs = data.get('images', [])
    if not imgs: imgs = ["assets/zodiac_signs/Pisces.jpg"]
    
    num_slices = max(4, len(imgs))
    slice_dur = duration / num_slices
    
    for i in range(num_slices):
        img_path = imgs[i % len(imgs)]
        if os.path.exists(img_path):
            img_clip = ImageClip(img_path).resize(width=1200)
            img_clip = img_clip.set_position('center')
            img_clip = apply_camera_motion(img_clip, slice_dur, i)
            img_clip = img_clip.set_start(i * slice_dur)
            
            # Smooth transitions
            if i > 0:
                img_clip = img_clip.crossfadein(0.4)
            if i < num_slices - 1:
                img_clip = img_clip.crossfadeout(0.4)
            
            clips.append(img_clip)
    
    # Color overlay for theme
    overlay_color = theme['overlay']
    overlay = ColorClip((1080, 1920), overlay_color[:3], duration=duration)
    overlay = overlay.set_opacity(overlay_color[3] / 255)
    clips.append(overlay)
    
    # Vignette effect
    vignette_path = create_vignette(1080, 1920)
    vignette = ImageClip(vignette_path).set_duration(duration)
    clips.append(vignette)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. PREMIUM ANIMATED SUBTITLES
    # ═══════════════════════════════════════════════════════════════════════════
    words = txt.split()
    # Create chunks of 3-4 words
    chunk_size = 3
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    # Calculate timing (leave 0.5s at start and end)
    subtitle_duration = duration - 1.0
    chunk_dur = subtitle_duration / len(chunks)
    
    for i, chunk in enumerate(chunks):
        start_time = 0.5 + (i * chunk_dur)
        sub_clip = create_animated_subtitle(
            chunk, 
            start_time, 
            chunk_dur, 
            theme['accent'],
            width=950
        )
        clips.append(sub_clip)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. FINAL COMPOSITION
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Combine all visuals
    final_video = CompositeVideoClip(clips, size=(1080, 1920))
    
    # Combine audio
    audio_clips = [voice_clip]
    if music:
        audio_clips.append(music)
    final_audio = CompositeAudioClip(audio_clips)
    
    # Set audio
    final_video = final_video.set_audio(final_audio)
    
    # Apply fade out at the end
    final_video = final_video.fadeout(0.5)
    
    # Write output (30fps for smoother feel)
    output_path = os.path.join("output_videos", f"{safe_title}.mp4")
    final_video.write_videofile(
        output_path, 
        fps=30, 
        preset='ultrafast',
        audio_codec='aac'
    )
    
    # Cleanup
    if os.path.exists("v.mp3"): os.remove("v.mp3")
    if os.path.exists("temp_vignette.png"): os.remove("temp_vignette.png")
    
    print(f"✅ PREMIUM VIDEO COMPLETE: {output_path}")
    return True

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    
    plan_files = [f for f in os.listdir('.') if f.startswith('plan_') and f.endswith('.json')]
    print(f"📂 Found {len(plan_files)} plans. Processing...")

    for p in plan_files:
        try:
            with open(p, 'r') as f: data = json.load(f)
            
            # Check flags
            if not data.get('active', True): 
                print(f"⏭️ SKIPPING (Inactive): {p}")
                continue
            if data.get('status') == 'done':
                print(f"✅ SKIPPING (Already Done): {p}")
                continue

            # Render
            success = render(p)

            # Update status
            if success:
                data['status'] = 'done'
                with open(p, 'w') as f: json.dump(data, f, indent=4)
                print(f"💾 Marked {p} as DONE.")
            
        except Exception as e:
            print(f"❌ Error processing {p}: {e}")
            import traceback
            traceback.print_exc()
