import os
import requests

DIRS = ["assets/music", "assets/fonts"]

# 1. Font: Cinzel (Reliable Google Fonts link)
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"

# 2. Music: Kevin MacLeod "Virtutes Instrumenti" (Reliable, Creative Commons, Dark/Mystical)
# Using a direct reliable MP3 source
MUSIC_URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Virtutes%20Instrumenti.mp3"

def download(url, path):
    print(f"⬇️ Downloading {path}...")
    try:
        # Fake browser headers to avoid 403 Forbidden
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=20)
        
        if r.status_code == 200:
            with open(path, 'wb') as f: f.write(r.content)
            
            # CHECK: Is the file real?
            if os.path.getsize(path) < 20000: # Less than 20KB is definitely not a song
                print(f"⚠️ File too small ({os.path.getsize(path)} bytes). Deleting.")
                os.remove(path)
            else:
                print("✅ Download Success.")
        else:
            print(f"❌ HTTP Error {r.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to download {path}: {e}")

def main():
    for d in DIRS:
        if not os.path.exists(d): os.makedirs(d)
    
    # Download Font
    if not os.path.exists("assets/fonts/Cinzel-Bold.ttf"):
        download(FONT_URL, "assets/fonts/Cinzel-Bold.ttf")
    
    # Download Music (Always retry if missing)
    if not os.path.exists("assets/music/mystical_bg.mp3"):
        download(MUSIC_URL, "assets/music/mystical_bg.mp3")

if __name__ == "__main__":
    main()
