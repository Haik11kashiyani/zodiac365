import json, os, subprocess
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    print(f"📼 Rendering {data['file_name']}...")

    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", data['script_text'], "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 2
    
    # Background
    clips = [ColorClip((1080, 1920), (5, 5, 10), duration=duration)]
    
    # LAYOUT LOGIC
    images = data.get('images', [])
    
    if data.get('type') == 'tarot':
        # 3 Cards Layout
        for i, path in enumerate(images):
            if os.path.exists(path):
                img = ImageClip(path).resize(width=900).set_pos("center").set_start(2 + i*5).set_duration(5).crossfadein(0.5)
                clips.append(img)
                
    elif data.get('type') == 'compatibility':
        # Split Screen Layout (VS)
        if len(images) >= 2 and os.path.exists(images[0]) and os.path.exists(images[1]):
            img1 = ImageClip(images[0]).resize(width=540).set_pos(('left', 'center')).set_duration(duration)
            img2 = ImageClip(images[1]).resize(width=540).set_pos(('right', 'center')).set_duration(duration)
            clips.append(img1)
            clips.append(img2)
            
            vs_text = TextClip("VS", fontsize=100, color='red', font="assets/fonts/Cinzel-Bold.ttf").set_pos('center').set_duration(duration)
            clips.append(vs_text)
            
    else:
        # Single Hero Image (Monthly/Yearly/Zodiac)
        if images and os.path.exists(images[0]):
            img = ImageClip(images[0]).resize(width=1080).set_pos("center").set_duration(duration).crossfadein(1)
            clips.append(img)

    # CTA
    cta = TextClip("thezodiacvault.kesug.com", fontsize=45, color='cyan', font="assets/fonts/Cinzel-Bold.ttf", method='caption', size=(900, None))
    clips.append(cta.set_pos(('center', 1600)).set_start(duration-5).set_duration(5))

    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.15).set_duration(duration)]))
    final.write_videofile(os.path.join("output_videos", data['file_name']), fps=24, preset='ultrafast')

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_')]
    for f in files: render(f)
