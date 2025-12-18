import os
import requests
import sys

# --- CONFIGURATION ---
ASSET_DIR = "assets/tarot_cards"
# Using a high-quality, pre-hosted cinematic deck to avoid AI generation timeouts
BASE_URL = "https://raw.githubusercontent.com/Haik11kashiyani/zodiac365/main/assets/tarot_cards/" 

def download_card(filename):
    save_path = os.path.join(ASSET_DIR, filename)
    if os.path.exists(save_path):
        return True
        
    url = f"https://www.sacred-texts.com/tarot/pkt/img/{filename}"
    # Re-mapping to standard filenames if needed, but for speed, we use a reliable archive
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        return False
    return False

def main():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)

    # Simplified Deck for reliable download
    cards = []
    for i in range(22): cards.append(f"ar{i:02d}.jpg") # Major Arcana
    
    print(f"🚀 Downloading stable assets to {ASSET_DIR}...")
    success = 0
    for card in cards:
        # Standardize naming to match your generator (m00.jpg, etc)
        our_name = card.replace("ar", "m")
        if download_card(card):
            os.rename(os.path.join(ASSET_DIR, card), os.path.join(ASSET_DIR, our_name))
            success += 1
            
    print(f"✅ Downloaded {success} stable assets.")

if __name__ == "__main__":
    main()
