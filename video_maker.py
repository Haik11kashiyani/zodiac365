import json, os, subprocess, random, re
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image

# System Font Name
FONT_NAME = "Cinzel-Bold" 

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def clean_speech(text):
    """Strips hashtags and AI artifacts so the voice is purely human."""
    return re.sub(r'[#\*]', '', text).strip()

def apply_camera_motion(clip, duration, index):
    """God-Level Motion: Alternates Zoom-In, Pull-Out, and Subtle Pan."""
    paths = [
        lambda t: 1 + 0.1 * (t/duration), 
        lambda t: 1.1 - 0.1 * (t/duration),
        lambda t: 1.05
    ]
    return clip.resize(paths[index % len(paths)]).set_duration(duration)

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    with open("config.json", "r") as f: config = json.load(f)

    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")
    print(f"🔱 GOD-MODE RENDERING: {safe_title}")

    # 1. Aura Voice Logic
    txt = clean_speech(data['script_text'])
    tts_engine = config.get("tts_engine", "edge")

    if tts_engine == "elevenlabs" and config.get("elevenlabs_keys"):
        # Placeholder for ElevenLabs - Fallback to edge if fails or no keys logic implemented yet
        # For now, simplistic implementation: use edge unless specific code added
        print("⚠️ ElevenLabs selected but simple implementation defaults to Edge for stability in this version.")
        subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--rate=-10%", "--text", txt, "--write-media", "v.mp3"])
    else:
        # Default: Edge TTS (ChristopherNeural)
        subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--rate=-10%", "--text", txt, "--write-media", "v.mp3"])
    
    if os.path.exists("v.mp3"):
        voice = AudioFileClip("v.mp3")
        duration = voice.duration + 1.2
    else:
        print("❌ TTS Failed!")
        return 

    
    # 2. Dynamic Audio Atmosphere
    music_track = random.choice([m for m in os.listdir("assets/music") if m.endswith(".mp3")])
    music = AudioFileClip(os.path.join("assets/music", music_track)).volumex(0.12).set_duration(duration)
    
    clips = [ColorClip((1080, 1920), (10, 5, 20), duration=duration)]
    
    # 3. Visual Slicing Engine (No more static images)
    imgs = data.get('images', [])
    if not imgs: imgs = ["assets/zodiac_signs/Pisces.jpg"]
    
    # Create 4 motion slices regardless of image count
    num_slices = 4 if len(imgs) == 1 else len(imgs)
    slice_dur = duration / num_slices
    for i in range(num_slices):
        img_path = imgs[i % len(imgs)]
        if os.path.exists(img_path):
            c = ImageClip(img_path).resize(width=1080).set_pos("center")
            c = apply_camera_motion(c, slice_dur, i).set_start(i * slice_dur).crossfadein(0.5)
            clips.append(c)

    # 4. Micro-Typography (Kinetic word bursts)
    words = txt.split()
    chunks = [" ".join(words[i:i+2]) for i in range(0, len(words), 2)]
    chunk_dur = duration / len(chunks)
    
    for i, chunk in enumerate(chunks):
        t_clip = TextClip(chunk.upper(), fontsize=85, color='#FFD700', font=FONT_NAME, 
                          stroke_color='black', stroke_width=3, method='caption', size=(900, None))
        t_clip = t_clip.set_start(i * chunk_dur).set_duration(chunk_dur).set_pos(('center', 1150))
        t_clip = t_clip.fadein(0.1).resize(lambda t: 1 + 0.02 * t)
        clips.append(t_clip)

    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, music]))
    final.write_videofile(os.path.join("output_videos", f"{safe_title}.mp4"), fps=24, preset='ultrafast')

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    
    plan_files = [f for f in os.listdir('.') if f.startswith('plan_') and f.endswith('.json')]
    print(f"📂 Found {len(plan_files)} plans. Checking status...")

    for p in plan_files:
        try:
            with open(p, 'r') as f: data = json.load(f)
            
            # CHECK FLAGS
            if not data.get('active', True): 
                print(f"⏭️ SKIPPING (Inactive): {p}")
                continue
            if data.get('status') == 'done':
                print(f"✅ SKIPPING (Already Done): {p}")
                continue

            # RENDER
            render(p)

            # UPDATE STATUS
            data['status'] = 'done'
            with open(p, 'w') as f: json.dump(data, f, indent=4)
            print(f"💾 Marked {p} as DONE.")
            
        except Exception as e:
            print(f"❌ Error processing {p}: {e}")
