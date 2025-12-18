import os, requests, sys

ASSET_DIR = "assets/tarot_cards"
# Using the Sacred Texts archive for high-speed, reliable card downloads
BASE_URL = "https://www.sacred-texts.com/tarot/pkt/img/"

def main():
    if not os.path.exists(ASSET_DIR): os.makedirs(ASSET_DIR)
    print("🚀 Downloading Stable Cinematic Tarot Deck...")
    
    success = 0
    # Downloading Major Arcana m00-m21 for the core loop
    for i in range(22):
        my_name = f"m{i:02d}.jpg"
        src_name = f"ar{i:02d}.jpg"
        path = os.path.join(ASSET_DIR, my_name)
        
        if not os.path.exists(path):
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get(BASE_URL + src_name, headers=headers, timeout=10)
                if r.status_code == 200:
                    with open(path, 'wb') as f: f.write(r.content)
                    success += 1
            except: continue
        else: success += 1

    print(f"✅ Assets Ready: {success}/22")
    if success < 15: sys.exit(1)

if __name__ == "__main__": main()
