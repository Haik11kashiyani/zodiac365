import os
import requests
import sys

# --- CONFIGURATION ---
ASSET_DIR = "assets/tarot_cards"
# Official Archive (Very Reliable)
BASE_URL = "https://www.sacred-texts.com/tarot/pkt/img/"

# Mapping: Our Code (01-14) <-> Sacred Texts (ac, 02..10, pa, kn, qu, ki)
# Sacred Texts Prefixes: ar=Major, wa=Wands, cu=Cups, sw=Swords, pe=Pentacles
SUIT_MAP = {'w': 'wa', 'c': 'cu', 's': 'sw', 'p': 'pe'}
RANK_MAP = {
    '01': 'ac', '02': '02', '03': '03', '04': '04', '05': '05', 
    '06': '06', '07': '07', '08': '08', '09': '09', '10': '10', 
    '11': 'pa', '12': 'kn', '13': 'qu', '14': 'ki'
}

def download_file(url, save_path):
    # User-Agent is required to avoid being blocked
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
        else:
            print(f"❌ HTTP {r.status_code}: {url}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

def main():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"📂 Created {ASSET_DIR}")

    print("🚀 Downloading & Remapping Tarot Assets...")
    success_count = 0
    total_needed = 78

    # 1. DOWNLOAD MAJOR ARCANA (m00 - m21) -> (ar00 - ar21)
    for i in range(22):
        my_name = f"m{i:02d}.jpg"
        src_name = f"ar{i:02d}.jpg"
        
        path = os.path.join(ASSET_DIR, my_name)
        if not os.path.exists(path):
            if download_file(BASE_URL + src_name, path):
                success_count += 1
        else:
            success_count += 1

    # 2. DOWNLOAD MINOR ARCANA
    for my_suit, src_suit in SUIT_MAP.items():
        for my_rank, src_rank in RANK_MAP.items():
            my_name = f"{my_suit}{my_rank}.jpg"   # e.g., w01.jpg
            src_name = f"{src_suit}{src_rank}.jpg" # e.g., waac.jpg
            
            path = os.path.join(ASSET_DIR, my_name)
            if not os.path.exists(path):
                if download_file(BASE_URL + src_name, path):
                    success_count += 1
            else:
                success_count += 1

    print(f"✅ Assets Report: {success_count}/{total_needed} images ready.")
    
    # FAIL SAFE: Crash if we don't have enough cards
    if success_count < 70:
        print("❌ CRITICAL: Assets failed. Check internet/URL.")
        sys.exit(1)

if __name__ == "__main__":
    main()
