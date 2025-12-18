import os
import requests

DIRS = ["assets/music", "assets/fonts"]
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"
MUSIC_URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Virtutes%20Instrumenti.mp3"

def download(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 10000:
        print(f"⬇️ Downloading {path}...")
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if r.status_code == 200: 
                with open(path, 'wb') as f: f.write(r.content)
        except: print(f"❌ Failed: {path}")

def main():
    for d in DIRS:
        if not os.path.exists(d): os.makedirs(d)
    download(FONT_URL, "assets/fonts/Cinzel-Bold.ttf")
    download(MUSIC_URL, "assets/music/mystical_bg.mp3")

if __name__ == "__main__":
    main()
