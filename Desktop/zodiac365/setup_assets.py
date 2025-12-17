import os
import requests
import time

# --- CONFIGURATION ---
ASSET_DIR = "assets/tarot_cards"
# We use a public GitHub repo that hosts these images (Rider Waite Deck)
BASE_URL = "https://raw.githubusercontent.com/tlenhardt/tarot-json/master/images/"

# List of cards files as named in the source repo
CARDS = [
    # Major Arcana
    "m00.jpg", "m01.jpg", "m02.jpg", "m03.jpg", "m04.jpg", "m05.jpg", 
    "m06.jpg", "m07.jpg", "m08.jpg", "m09.jpg", "m10.jpg", "m11.jpg", 
    "m12.jpg", "m13.jpg", "m14.jpg", "m15.jpg", "m16.jpg", "m17.jpg", 
    "m18.jpg", "m19.jpg", "m20.jpg", "m21.jpg",
    # Cups
    "c01.jpg", "c02.jpg", "c03.jpg", "c04.jpg", "c05.jpg", "c06.jpg", "c07.jpg", "c08.jpg", "c09.jpg", "c10.jpg", "c11.jpg", "c12.jpg", "c13.jpg", "c14.jpg",
    # Pentacles
    "p01.jpg", "p02.jpg", "p03.jpg", "p04.jpg", "p05.jpg", "p06.jpg", "p07.jpg", "p08.jpg", "p09.jpg", "p10.jpg", "p11.jpg", "p12.jpg", "p13.jpg", "p14.jpg",
    # Swords
    "s01.jpg", "s02.jpg", "s03.jpg", "s04.jpg", "s05.jpg", "s06.jpg", "s07.jpg", "s08.jpg", "s09.jpg", "s10.jpg", "s11.jpg", "s12.jpg", "s13.jpg", "s14.jpg",
    # Wands
    "w01.jpg", "w02.jpg", "w03.jpg", "w04.jpg", "w05.jpg", "w06.jpg", "w07.jpg", "w08.jpg", "w09.jpg", "w10.jpg", "w11.jpg", "w12.jpg", "w13.jpg", "w14.jpg"
]

def download_file(url, filepath):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Downloaded: {filepath}")
        else:
            print(f"❌ Failed: {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    # 1. Create Directory
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"📂 Created directory: {ASSET_DIR}")

    # 2. Download Cards
    print("🚀 Starting download of 78 Tarot Cards...")
    for filename in CARDS:
        url = BASE_URL + filename
        # We rename them to be cleaner (e.g., m00.jpg -> the_fool.jpg) strictly? 
        # No, let's keep it simple for the machine first.
        save_path = os.path.join(ASSET_DIR, filename)
        
        if not os.path.exists(save_path):
            download_file(url, save_path)
            time.sleep(0.1) # Be nice to the server
        else:
            print(f"⚡ Skipping {filename} (Already exists)")

    print("\n🎉 All Assets Ready. You are ready for Video Production.")

if __name__ == "__main__":
    main()