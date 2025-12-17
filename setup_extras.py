import os
import requests

# --- CONFIGURATION ---
DIRS = ["assets/music", "assets/fonts"]
# Royalty-free music file (Dark Ambient)
MUSIC_URL = "https://cdn.pixabay.com/download/audio/2022/10/25/audio_b20c95022e.mp3?filename=mystery-125324.mp3" 
# Google Font (Cinzel - looks very astrological)
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"

def download_file(url, filepath):
    print(f"⬇️ Downloading: {filepath}...")
    try:
        response = requests.get(url)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print("✅ Done.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    # 1. Create Directories
    for d in DIRS:
        if not os.path.exists(d):
            os.makedirs(d)

    # 2. Download Music
    music_path = "assets/music/mystical_bg.mp3"
    if not os.path.exists(music_path):
        download_file(MUSIC_URL, music_path)
    else:
        print("⚡ Music already exists.")

    # 3. Download Font
    font_path = "assets/fonts/Cinzel-Bold.ttf"
    if not os.path.exists(font_path):
        download_file(FONT_URL, font_path)
    else:
        print("⚡ Font already exists.")

if __name__ == "__main__":
    main()
