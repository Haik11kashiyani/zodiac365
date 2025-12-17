import os
import requests

# --- CONFIGURATION ---
DIRS = ["assets/music", "assets/fonts"]

# 1. Google Font (Cinzel - Cinematic & Mystical)
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"

# 2. Background Music (Dark Ambient)
# Using a reliable raw GitHub link for a royalty-free track to avoid expire links
MUSIC_URL = "https://github.com/Haik11kashiyani/zodiac365/releases/download/assets/mystical_bg.mp3"
# FALLBACK: If you haven't uploaded one, use this generic placeholder or upload your own "mystical_bg.mp3" to assets/music/
# For now, let's try a direct reliable open source file:
MUSIC_URL_BACKUP = "https://upload.wikimedia.org/wikipedia/commons/5/5e/Dark_Ambience.ogg" 

def download_file(url, filepath):
    print(f"⬇️ Downloading: {filepath}...")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("✅ Done.")
        else:
            print(f"❌ Failed to download {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    # 1. Create Directories
    for d in DIRS:
        if not os.path.exists(d):
            os.makedirs(d)

    # 2. Download Font
    font_path = "assets/fonts/Cinzel-Bold.ttf"
    if not os.path.exists(font_path):
        download_file(FONT_URL, font_path)
    else:
        print("⚡ Font already exists.")

    # 3. Download Music
    music_path = "assets/music/mystical_bg.mp3"
    if not os.path.exists(music_path):
        print("🎵 Downloading Background Music...")
        # Try primary (if you uploaded one), else backup
        try:
            download_file(MUSIC_URL_BACKUP, music_path)
        except:
            print("⚠️ Could not download music. Please upload 'mystical_bg.mp3' to assets/music/ manually.")
    else:
        print("⚡ Music already exists.")

if __name__ == "__main__":
    main()
