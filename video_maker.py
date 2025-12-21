import json, os, subprocess, random, re, math
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image, ImageDraw
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════════
# WESTERN VIRAL VIDEO MAKER v4.0
# Professional editing for international audiences
# ═══════════════════════════════════════════════════════════════════════════════

FONT_NAME = "Montserrat-Bold"

VOICE_POOL = [
    "en-US-ChristopherNeural",
    "en-US-GuyNeural", 
    "en-US-DavisNeural",
]

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
# TEXT CLEANING
# ═══════════════════════════════════════════════════════════════════════════════

def clean_speech(text):
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'[#\*]', '', text)
    text = re.sub(r':\s*', '. ', text)
    text = re.sub(r'["""\'\'`]', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_subtitle(text):
    text = clean_speech(text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_vignette(width, height):
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    vignette = np.clip((R - 0.5) / 0.9, 0, 1) * 200
    vignette = vignette.astype(np.uint8)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    alpha = Image.fromarray(vignette)
    img.putalpha(alpha)
    path = "temp_vignette.png"
    img.save(path)
    return path

def create_subtitle_bg(width, height, opacity=180):
    """Create a rounded rectangle background for subtitles."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Rounded rectangle
    radius = 20
    draw.rounded_rectangle([0, 0, width-1, height-1], radius=radius, fill=(0, 0, 0, opacity))
    path = "temp_subtitle_bg.png"
    img.save(path)
    return path

def apply_camera_motion(clip, duration, motion_type):
    if motion_type == 0:  # Zoom In
        return clip.resize(lambda t: 1 + 0.2 * (t/duration)).set_duration(duration)
    elif motion_type == 1:  # Zoom Out
        return clip.resize(lambda t: 1.2 - 0.2 * (t/duration)).set_duration(duration)
    elif motion_type == 2:  # Pan Right
        def pos(t): return (-80 + 160 * (t/duration), 'center')
        return clip.set_position(pos).set_duration(duration)
    elif motion_type == 3:  # Pan Down
        def pos(t): return ('center', -80 + 160 * (t/duration))
        return clip.set_position(pos).set_duration(duration)
    elif motion_type == 4:  # Pulse Zoom
        return clip.resize(lambda t: 1.08 + 0.04 * math.sin(t * 3)).set_duration(duration)
    else:  # Drift
        return clip.resize(lambda t: 1.1 + 0.03 * t).set_duration(duration)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ═══════════════════════════════════════════════════════════════════════════════

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    
    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")[:50]
    print(f"🔱 RENDERING: {safe_title}")

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. VOICE GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    txt = clean_speech(data['script_text'])
    voice = random.choice(VOICE_POOL)
    rate = random.choice(["-5%", "-8%"])
    
    print(f"   Voice: {voice} | Rate: {rate}")
    
    try:
        subprocess.run([
            "edge-tts", "--voice", voice, f"--rate={rate}",
            "--text", txt, "--write-media", "v.mp3"
        ], capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"   ⚠️ TTS Error: {e}")
    
    if not os.path.exists("v.mp3") or os.path.getsize("v.mp3") < 1000:
        print("❌ TTS Failed!")
        return False
    
    voice_clip = AudioFileClip("v.mp3")
    duration = voice_clip.duration + 0.8
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. AUDIO MIX (Music + SFX)
    # ═══════════════════════════════════════════════════════════════════════════
    audio_clips = [voice_clip]
    
    # Background music
    music_files = [m for m in os.listdir("assets/music") if m.endswith(".mp3")]
    if music_files:
        music = AudioFileClip(os.path.join("assets/music", random.choice(music_files)))
        music = music.volumex(0.06).set_duration(duration)
        audio_clips.append(music)
    
    # Whoosh SFX at transitions
    whoosh_path = "assets/sfx/whoosh.mp3"
    if os.path.exists(whoosh_path):
        try:
            whoosh = AudioFileClip(whoosh_path).volumex(0.3)
            # Add whoosh at 2-3 points
            for t in [duration * 0.25, duration * 0.5, duration * 0.75]:
                audio_clips.append(whoosh.set_start(t))
        except:
            pass
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. VISUAL COMPOSITION
    # ═══════════════════════════════════════════════════════════════════════════
    clips = []
    
    # Dark base
    base = ColorClip((1080, 1920), (8, 5, 15), duration=duration)
    clips.append(base)
    
    # Images with motion
    main_imgs = data.get('images', [])
    if not main_imgs:
        main_imgs = [random.choice(ALL_ZODIAC_IMAGES)]
    
    available_extras = [i for i in ALL_ZODIAC_IMAGES if i not in main_imgs and os.path.exists(i)]
    extra_imgs = random.sample(available_extras, min(2, len(available_extras)))
    all_imgs = main_imgs + extra_imgs
    
    # Fast-paced segments (Western style)
    num_segments = 5
    segment_dur = duration / num_segments
    
    for i in range(num_segments):
        img_path = all_imgs[i % len(all_imgs)]
        if not os.path.exists(img_path):
            continue
        
        img_clip = ImageClip(img_path).resize(height=2300)
        img_clip = img_clip.set_position('center')
        img_clip = apply_camera_motion(img_clip, segment_dur, i % 6)
        img_clip = img_clip.set_start(i * segment_dur)
        
        # Quick crossfade
        if i > 0:
            img_clip = img_clip.crossfadein(0.3)
        
        clips.append(img_clip)
    
    # Dark overlay for readability
    overlay = ColorClip((1080, 1920), (0, 0, 0), duration=duration).set_opacity(0.35)
    clips.append(overlay)
    
    # Vignette
    vignette_path = create_vignette(1080, 1920)
    vignette = ImageClip(vignette_path).set_duration(duration)
    clips.append(vignette)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. SUBTITLES WITH BACKGROUND BOX
    # ═══════════════════════════════════════════════════════════════════════════
    subtitle_text = clean_subtitle(txt)
    words = subtitle_text.split()
    chunk_size = 4
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    if chunks:
        voice_dur = voice_clip.duration
        chunk_dur = voice_dur / len(chunks)
        
        print(f"   📝 {len(chunks)} subtitles")
        
        # Create subtitle background once
        sub_bg_path = create_subtitle_bg(950, 120, opacity=160)
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            start_time = i * chunk_dur
            
            try:
                # Background box
                bg_clip = ImageClip(sub_bg_path)
                bg_clip = bg_clip.set_position(('center', 1250))
                bg_clip = bg_clip.set_start(start_time).set_duration(chunk_dur)
                bg_clip = bg_clip.crossfadein(0.08).crossfadeout(0.08)
                clips.append(bg_clip)
                
                # Text on top
                text_clip = TextClip(
                    chunk.upper(),
                    fontsize=55,
                    color='white',
                    font=FONT_NAME,
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(900, None)
                )
                text_clip = text_clip.set_position(('center', 1260))
                text_clip = text_clip.set_start(start_time).set_duration(chunk_dur)
                text_clip = text_clip.crossfadein(0.08).crossfadeout(0.08)
                clips.append(text_clip)
                
            except Exception as e:
                print(f"   ⚠️ Subtitle {i}: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. FINAL OUTPUT
    # ═══════════════════════════════════════════════════════════════════════════
    final_video = CompositeVideoClip(clips, size=(1080, 1920))
    final_audio = CompositeAudioClip(audio_clips)
    final_video = final_video.set_audio(final_audio)
    final_video = final_video.fadeout(0.4)
    
    output_path = os.path.join("output_videos", f"{safe_title}.mp4")
    final_video.write_videofile(output_path, fps=30, preset='ultrafast', audio_codec='aac')
    
    # Cleanup
    for f in ["v.mp3", "temp_vignette.png", "temp_subtitle_bg.png"]:
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
                print(f"⏭️ SKIP: {p}")
                continue
            if data.get('status') == 'done':
                print(f"✅ SKIP: {p}")
                continue

            success = render(p)
            
            if success:
                data['status'] = 'done'
                with open(p, 'w') as f: json.dump(data, f, indent=4)
                print(f"💾 Marked DONE: {p}")
            
        except Exception as e:
            print(f"❌ Error {p}: {e}")
            import traceback
            traceback.print_exc()
