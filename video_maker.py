import json, os, subprocess
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", data['script_text'], "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 1
    
    clips = [ColorClip((1080, 1920), (5, 5, 15), duration=duration)]
    
    # Hero Images
    for i, path in enumerate(data.get('images', [])):
        if os.path.exists(path):
            img = ImageClip(path).resize(width=1080).set_pos("center").set_duration(duration).crossfadein(1)
            clips.append(img)

    # Dynamic Subtitles
    for ol in data.get('overlays', []):
        txt = TextClip(ol['text'].upper(), fontsize=85, color='gold', font="assets/fonts/Cinzel-Bold.ttf", stroke_color='black', stroke_width=2)
        start = 0 if ol['time'] == 'start' else (duration/2 if ol['time'] == 'middle' else duration-4)
        clips.append(txt.set_pos('center').set_start(start).set_duration(3).crossfadein(0.5))

    # Static Website CTA
    website = TextClip("thezodiacvault.kesug.com", fontsize=45, color='cyan', font="assets/fonts/Cinzel-Bold.ttf").set_pos(('center', 1650)).set_duration(duration)
    clips.append(website)

    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.12).set_duration(duration)]))
    final.write_videofile(os.path.join("output_videos", data['title'].replace(" ", "_") + ".mp4"), fps=24, preset='ultrafast')

if __name__ == "__main__":
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]: render(f)
