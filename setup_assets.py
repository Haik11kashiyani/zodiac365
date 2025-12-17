import os
import requests
import sys

# --- CONFIGURATION ---
ASSET_DIR = "assets/tarot_cards"
# The "Sacred Texts" Archive (Never deletes files)
BASE_URL = "https://www.sacred-texts.com/tarot/pkt/img/"

# MAPPING: Sacred Texts Name -> Our Name
# They use 'cuac' for Ace of Cups, we need 'c01'
SUIT_MAP = {'wa': 'w', 'cu': 'c', 'sw': 's', 'pe': 'p'}
RANK_MAP = {
    'ac': '01', '02': '02', '03': '03', '04': '04', '05': '05', 
    '06': '06', '07': '07', '08': '08', '09': '09', '10': '10', 
    'pa': '11', 'kn': '12', 'qu': '13', 'ki': '14'
}

def download_file(url, save_path):
    # Fake a browser to avoid blocks
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
        else:
            print(f"❌ HTTP {r.status_code} for {url}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

def main():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"📂 Created {ASSET_DIR}")

    print("🚀 Downloading Assets from Sacred Texts...")
    success_count = 0
    
    # 1. MAJOR ARCANA (ar00.jpg -> m00.jpg)
    for i in range(22):
        src_name = f"ar{i:02d}.jpg"
        dst_name = f"m{i:02d}.jpg"
        
        save_path = os.path.join(ASSET_DIR, dst_name)
        if not os.path.exists(save_path):
            if download_file(BASE_URL + src_name, save_path):
                success_count += 1
        else:
            success_count += 1

    # 2. MINOR ARCANA (cuac.jpg -> c01.jpg)
    for src_suit, dst_suit in SUIT_MAP.items():
        for src_rank, dst_rank in RANK_MAP.items():
            src_name = f"{src_suit}{src_rank}.jpg"
            dst_name = f"{dst_suit}{dst_rank}.jpg"
            
            save_path = os.path.join(ASSET_DIR, dst_name)
            if not os.path.exists(save_path):
                if download_file(BASE_URL + src_name, save_path):
                    success_count += 1
            else:
                success_count += 1

    print(f"✅ Assets Ready: {success_count}/78")
    
    # CRITICAL CHECK
    if success_count < 70:
        print("❌ FATAL: Assets failed to download.")
        sys.exit(1)

if __name__ == "__main__":
    main()
