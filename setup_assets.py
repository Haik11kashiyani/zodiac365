import os
import requests
import time
import sys
from urllib.parse import quote

# --- CONFIGURATION ---
ASSET_DIR = "assets/tarot_cards"
BASE_URL = "https://image.pollinations.ai/prompt/"
STYLE = "mystical tarot card, dark fantasy art, golden intricate details, glowing magic, 8k resolution, cinematic lighting, masterpiece, vertical ratio"

def generate_image(prompt, filename):
    save_path = os.path.join(ASSET_DIR, filename)
    
    # 1. SKIP IF EXISTS (Smart Resume)
    if os.path.exists(save_path) and os.path.getsize(save_path) > 10000:
        print(f"⚡ Skipping {filename} (Already exists)")
        return True

    full_prompt = quote(f"{prompt}, {STYLE}")
    url = f"{BASE_URL}{full_prompt}?width=1080&height=1920&nologo=true&model=flux"
    
    # 2. RETRY LOOP (Try 3 times)
    for attempt in range(1, 4):
        try:
            print(f"🎨 Painting: {filename} (Attempt {attempt}/3)...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, timeout=60)
            
            if r.status_code == 200:
                with open(save_path, 'wb') as f: f.write(r.content)
                print(f"✅ Saved: {filename}")
                time.sleep(2) # Pause to prevent blocking
                return True
            elif r.status_code == 429:
                print("⚠️ Rate Limited. Sleeping 10s...")
                time.sleep(10)
            else:
                print(f"⚠️ Error {r.status_code}")
                
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            time.sleep(5)
            
    print(f"❌ Failed to generate {filename} after 3 attempts.")
    return False

def main():
    if not os.path.exists(ASSET_DIR): os.makedirs(ASSET_DIR)

    cards = []
    majors = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]
    for i, name in enumerate(majors): cards.append((name, f"m{i:02d}.jpg"))

    suits = {"Wands": "w", "Cups": "c", "Swords": "s", "Pentacles": "p"}
    ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
    for s_name, s_code in suits.items():
        for i, r_name in enumerate(ranks):
            cards.append((f"{r_name} of {s_name}", f"{s_code}{i+1:02d}.jpg"))

    success = 0
    print(f"🚀 Verifying {len(cards)} AI Images...")
    for name, filename in cards:
        if generate_image(name, filename): success += 1
    
    print(f"📊 Gallery Status: {success}/{len(cards)} ready.")
    
    # Allow passing if most cards are there (prevents total block)
    if success < 60:
        print("❌ CRITICAL: Too many assets missing. Pipeline stopped.")
        sys.exit(1)

if __name__ == "__main__":
    main()
