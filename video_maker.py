import json, os, subprocess
from moviepy.config import change_settings
from moviepy.editor import *
from PIL import Image

if not hasattr(Image, 'ANTIALIAS'): Image.ANTIALIAS = Image.LANCZOS
if os.name == 'posix': change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render(plan_file):
    with open(plan_file, 'r') as f: data = json.load(f)
    script = data.get('script_text', '')
    
    # Generate Neural Voice
    subprocess.run(["edge-tts", "--voice", "en-US-ChristopherNeural", "--text", script, "--write-media", "v.mp3"])
    voice = AudioFileClip("v.mp3")
    duration = voice.duration + 1
    
    clips = [ColorClip((1080, 1920), (5, 5, 15), duration=duration)]
    
    # Hero Visuals
    imgs = data.get('images', [])
    if imgs:
        for i, path in enumerate(imgs):
            if os.path.exists(path):
                img = ImageClip(path).resize(width=1080).set_pos("center").set_duration(duration).crossfadein(1)
                clips.append(img)
    else:
        # Fallback if no specific image exists (for Special Insights)
        bg = ColorClip((1080, 1920), (20, 10, 40), duration=duration)
        clips.append(bg)

    # Text Overlays
    font = "assets/fonts/Cinzel-Bold.ttf"
    for ol in data.get('overlays', []):
        txt = TextClip(ol['text'].upper(), fontsize=80, color='gold', font=font, stroke_color='black', stroke_width=2)
        start = 0 if ol['time'] == 'start' else (duration/2 if ol['time'] == 'middle' else duration-4)
        clips.append(txt.set_pos('center').set_start(start).set_duration(3).crossfadein(0.5))

    # Website Link
    website = TextClip("thezodiacvault.kesug.com", fontsize=45, color='cyan', font=font).set_pos(('center', 1650)).set_duration(duration)
    clips.append(website)

    final = CompositeVideoClip(clips).set_audio(CompositeAudioClip([voice, AudioFileClip("assets/music/mystical_bg.mp3").volumex(0.12).set_duration(duration)]))
    final.write_videofile(os.path.join("output_videos", data['title'].replace(" ", "_") + ".mp4"), fps=24, preset='ultrafast')

if __name__ == "__main__":
    if not os.path.exists("output_videos"): os.makedirs("output_videos")
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]: render(f)
