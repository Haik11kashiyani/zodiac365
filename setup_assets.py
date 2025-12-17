import os
import requests
import sys

ASSET_DIR = "assets/tarot_cards"
BASE_URL = "https://raw.githubusercontent.com/tlenhardt/tarot-json/master/images/"

def main():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)

    print("🚀 Downloading Tarot Cards...")
    
    # Generate list of needed files (m00-m21, w01-w14, etc.)
    cards = []
    for i in range(22): cards.append(f"m{i:02d}.jpg")
    for s in ['w', 'c', 's', 'p']:
        for i in range(1, 15): cards.append(f"{s}{i:02d}.jpg")

    success = 0
    for card in cards:
        path = os.path.join(ASSET_DIR, card)
        if not os.path.exists(path):
            try:
                r = requests.get(BASE_URL + card, timeout=10)
                if r.status_code == 200:
                    with open(path, 'wb') as f: f.write(r.content)
                    if os.path.getsize(path) > 1000: success += 1
            except: pass
        else:
            success += 1

    print(f"✅ Assets Ready: {success}/{len(cards)}")
    if success < 70:
        print("❌ CRITICAL: Failed to download cards.")
        sys.exit(1)

if __name__ == "__main__":
    main()
