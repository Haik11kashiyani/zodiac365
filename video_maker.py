import json, os, subprocess, random, re
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image

# Use the System-Registered Name fixed in our YAML
FONT_NAME = "Cinzel-Bold" 

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def clean_speech(text):
    return re.sub(r'[#\*]', '', text).strip()

def apply_camera_motion(clip, duration, index):
    """God-Level Motion: Alternates between 4 different cinematic paths."""
    paths = [
        lambda t: 1 + 0.1 * (t/duration),    # Zoom In
        lambda t: 1.1 - 0.1 * (t/duration),  # Pull Out
        lambda t: 1.05                       # Static Scale
    ]
    return clip.resize(paths[index % len(paths)]).set_duration(duration)

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    safe_title = re.sub(r'[\\/*?:"<>|]', "", data['title']).replace(" ", "_")
    print(f"🔱 RENDERING: {safe_title}")

    # 1. Slowed Human Voice (-10% for authority)
    txt = clean_speech(data['script_text'])
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--rate=-10%", "--text", txt, "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 1.0
    
    # 2. Random Music Selection
    music_files = [f for f in os.listdir("assets/music") if f.endswith(".mp3")]
    music_track = random.choice(music_files) if music_files else "mystical_main.mp3"
    music = AudioFileClip(os.path.join("assets/music", music_track)).volumex(0.12).set_duration(duration)
    
    clips = [ColorClip((1080, 1920), (10, 5, 20), duration=duration)]
    
    # 3. Visual Slicing Engine (Fixes 'One Image' issue)
    imgs = data.get('images', [])
    if not imgs: imgs = [os.path.join("assets/zodiac_signs", "Aries.jpg")]
    
    # Create 4 motion slices even if we only have one image
    num_slices = 4 if len(imgs) == 1 else len(imgs)
    slice_dur = duration / num_slices
    for i in range(num_slices):
        img_path = imgs[i % len(imgs)]
        if os.path.exists(img_path):
            c = ImageClip(img_path).resize(width=1080).set_pos("center")
            c = apply_camera_motion(c, slice_dur, i).set_start(i * slice_dur).crossfadein(0.5)
            clips.append(c)

    # 4. Kinetic Typography (Small, Proper Subtitles)
    words = txt.split()
    chunk_size = 2 # Best for modern retention
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    chunk_dur = duration / len(chunks)
    
    for i, chunk in enumerate(chunks):
        t_clip = TextClip(chunk.upper(), fontsize=85, color='#FFD700', font=FONT_NAME, 
                          stroke_color='black', stroke_width=3, method='caption', size=(900, None))
        t_clip = t_clip.set_start(i * chunk_dur).set_duration(chunk_dur).set_pos(('center', 1150))
        t_clip = t_clip.fadein(0.1).resize(lambda t: 1 + 0.02 * t)
        clips.append(t_clip)

    # 5. Final Brand
    brand = TextClip("thezodiacvault.kesug.com", fontsize=35, color='cyan', font=FONT_NAME)
    clips.append(brand.set_pos(('center', 1780)).set_duration(duration).set_opacity(0.6))

    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, music]))
    final.write_videofile(os.path.join("output_videos", f"{safe_title}.mp4"), fps=24, preset='ultrafast')

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    for p in [f for f in os.listdir('.') if f.startswith('plan_')]: render(p)
