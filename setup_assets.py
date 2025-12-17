import os
import requests
import sys

ASSET_DIR = "assets/tarot_cards"
# Using a fast, public GitHub mirror for reliability
BASE_URL = "https://raw.githubusercontent.com/tlenhardt/tarot-json/master/images/"

def main():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)

    print("🚀 Downloading Tarot Cards...")
    
    # Files needed: m00-m21, w01-w14, etc.
    cards = []
    for i in range(22): cards.append(f"m{i:02d}.jpg")
    for s in ['w', 'c', 's', 'p']:
        for i in range(1, 15): cards.append(f"{s}{i:02d}.jpg")

    success = 0
    # Headers make us look like a real browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for card in cards:
        path = os.path.join(ASSET_DIR, card)
        
        # Download if missing OR if file is empty (0 bytes)
        if not os.path.exists(path) or os.path.getsize(path) < 100:
            try:
                r = requests.get(BASE_URL + card, headers=headers, timeout=10)
                if r.status_code == 200:
                    with open(path, 'wb') as f: f.write(r.content)
                    success += 1
                else:
                    print(f"❌ Failed: {card} (Status {r.status_code})")
            except Exception as e:
                print(f"❌ Error: {card} - {e}")
        else:
            success += 1

    print(f"✅ Assets Ready: {success}/{len(cards)}")
    
    # Critical Check
    if success < 70:
        print("❌ CRITICAL: Failed to download cards. Check Internet.")
        sys.exit(1)

if __name__ == "__main__":
    main()
