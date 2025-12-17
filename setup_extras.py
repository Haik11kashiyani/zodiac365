import os
import requests

DIRS = ["assets/music", "assets/fonts"]
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"
MUSIC_URL = "https://upload.wikimedia.org/wikipedia/commons/5/5e/Dark_Ambience.ogg"

def download(url, path):
    if not os.path.exists(path):
        print(f"⬇️ Downloading {path}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            with open(path, 'wb') as f: f.write(r.content)
        except: print(f"❌ Failed to download {path}")

def main():
    for d in DIRS:
        if not os.path.exists(d): os.makedirs(d)
    
    download(FONT_URL, "assets/fonts/Cinzel-Bold.ttf")
    download(MUSIC_URL, "assets/music/mystical_bg.mp3")

if __name__ == "__main__":
    main()
