import json, os, subprocess, random, re, math, textwrap
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

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

def create_glow_box(width, height, box_width=900, box_height=150):
    """Create a box for subtitles."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Coordinates
    x1 = (width - box_width) // 2
    y1 = 1250
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
    """Find images that actually match the sign/topic."""
    title = data.get('title', '')
    target = data.get('target', '') # Might not exist in json, checking title/file_name
    fname = data.get('file_name', '')
    
    # Identify sign
    found_signs = []
    for sign, path in ZODIAC_SIGNS.items():
        if sign in title or sign in fname:
            found_signs.append(path)
    
    # Use found signs first
    images = []
    if found_signs:
        images.extend(found_signs)
        # Duplicate for length if needed, or add related tarot cards?
        # Let's add Tarot cards as fallback/variety
    
    # Fallback to provided images in data
    if not images:
        images = data.get('images', [])
    
    # If still empty, randomly pick ONE sign (risky but better than crash)
    if not images:
        images = [random.choice(list(ZODIAC_SIGNS.values()))]
        
    # Add generic "mystical" tarot cards for variety (never other signs)
    tarot_dir = "assets/tarot_cards"
    if os.path.exists(tarot_dir):
        tarot_cards = [os.path.join(tarot_dir, f) for f in os.listdir(tarot_dir) if f.endswith('.jpg')]
        if tarot_cards:
            images.extend(random.sample(tarot_cards, min(3, len(tarot_cards))))
            
    return images

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")[:50]
    print(f"🔱 RENDERING: {safe_title}")

    # 1. VOICE
    txt = clean_speech(data['script_text'])
    voice = random.choice(VOICE_POOL)
    rate = random.choice(["-5%", "-8%"]) # Simple rate
    
    print(f"   Voice: {voice}")
    
    try:
        subprocess.run([
            "edge-tts", "--voice", voice, f"--rate={rate}",
            "--text", txt, "--write-media", "v.mp3"
        ], capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"   ⚠️ TTS Error: {e}")
        return False
        
    if not os.path.exists("v.mp3") or os.path.getsize("v.mp3") < 1000:
        return False
        
    voice_clip = AudioFileClip("v.mp3")
    duration = voice_clip.duration + 1.0

    # 2. AUDIO MIX
    audio_clips = [voice_clip]
    music_files = [m for m in os.listdir("assets/music") if m.endswith(".mp3")]
    if music_files:
        music = AudioFileClip(os.path.join("assets/music", random.choice(music_files)))
        music = music.volumex(0.08).set_duration(duration) # Slight boost to 0.08
        audio_clips.append(music)
    
    # SFX
    whoosh_path = "assets/sfx/whoosh.mp3"
    riser_path = "assets/sfx/riser.mp3"
    
    whoosh = AudioFileClip(whoosh_path).volumex(0.4) if os.path.exists(whoosh_path) else None
    
    # 3. VISUALS
    clips = []
    base = ColorClip((1080, 1920), (5, 5, 10), duration=duration)
    clips.append(base)
    
    # Images
    images = get_relevant_images(data)
    # Ensure we cycle through them
    num_segments = 5
    seg_dur = duration / num_segments
    
    for i in range(num_segments):
        img_path = images[i % len(images)]
        if not os.path.exists(img_path): continue
        
        img_clip = ImageClip(img_path).resize(height=2300)
        img_clip = img_clip.set_position('center')
        
        # Motion
        m_type = i % 5
        if m_type == 0: img_clip = img_clip.resize(lambda t: 1+0.1*t/seg_dur)
        elif m_type == 1: img_clip = img_clip.resize(lambda t: 1.1-0.1*t/seg_dur)
        elif m_type == 2: img_clip = img_clip.set_position(lambda t: (-50+100*t/seg_dur, 'center'))
        elif m_type == 3: img_clip = img_clip.resize(lambda t: 1.05+0.03*math.sin(t*2))
        else: img_clip = img_clip.resize(lambda t: 1.1) 
        
        img_clip = img_clip.set_start(i * seg_dur).set_duration(seg_dur)
        if i > 0: img_clip = img_clip.crossfadein(0.3)
        clips.append(img_clip)
        
        # Audio Whoosh on cut
        if i > 0 and whoosh:
            audio_clips.append(whoosh.set_start(i * seg_dur))

    # Overlays
    # Particle/Noise
    particle_path = create_particle_overlay(1080, 1920)
    particles = ImageClip(particle_path).set_duration(duration).set_opacity(0.15)
    clips.append(particles)
    
    # Dark Overlay for text
    overlay = ColorClip((1080, 1920), (0,0,0), duration=duration).set_opacity(0.3)
    clips.append(overlay)
    
    # Vignette
    vignette_path = create_vignette(1080, 1920)
    vignette = ImageClip(vignette_path).set_duration(duration)
    clips.append(vignette)
    
    # 4. SUBTITLES
    subtitle_text = clean_subtitle(txt)
    words = subtitle_text.split()
    chunk_size = 4
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    if chunks:
        chunk_dur = voice_clip.duration / len(chunks)
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip(): continue
            start = i * chunk_dur
            
            # WRAPPED TEXT
            wrapped = wrap_text_dynamic(chunk.upper(), max_char=18)
            num_lines = wrapped.count('\n') + 1
            
            # Dynamic Box Height
            box_h = 140 if num_lines == 1 else 220
            box_path = create_glow_box(1080, 1920, box_height=box_h)
            
            bg = ImageClip(box_path).set_start(start).set_duration(chunk_dur)
            bg = bg.crossfadein(0.05).crossfadeout(0.05)
            clips.append(bg)
            
            txt_clip = TextClip(
                wrapped, 
                fontsize=70, 
                color='yellow', 
                font=FONT_NAME,
                stroke_color='black', 
                stroke_width=3,
                method='caption',
                align='center',
                size=(900, None)
            )
            txt_clip = txt_clip.set_position(('center', 1280 + (10 if num_lines==1 else 0)))
            txt_clip = txt_clip.set_start(start).set_duration(chunk_dur)
            clips.append(txt_clip)

    # 5. FINAL
    final = CompositeVideoClip(clips, size=(1080, 1920))
    final = final.set_audio(CompositeAudioClip(audio_clips))
    final = final.fadeout(0.5)
    
    output_path = os.path.join("output_videos", f"{safe_title}.mp4")
    final.write_videofile(output_path, fps=30, preset='ultrafast', audio_codec='aac')
    
    # cleanup
    for f in ["v.mp3", "temp_vignette.png", "temp_sub_box.png", "temp_particles.png"]:
        if os.path.exists(f): os.remove(f)
    return True

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    plan_files = [f for f in os.listdir('.') if f.startswith('plan_') and f.endswith('.json')]
    for p in plan_files:
        try:
            with open(p, 'r') as f: data = json.load(f)
            if not data.get('active', True) or data.get('status') == 'done': continue
            if render(p):
                data['status'] = 'done'
                with open(p, 'w') as f: json.dump(data, f, indent=4)
        except Exception as e: print(e)
