import os
import requests
import time
import shutil
import sys

# Force UTF-8 (Removed as it causes issues in some shells)
# sys.stdout.reconfigure(encoding='utf-8')

# --- CONFIGURATION ---
ASSET_DIR = "assets/zodiac_signs"
THEME = "mystical dark golden astrology zodiac sign, cinematic lighting, 8k, hyperrealistic"

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


# Valid Styles for variety
STYLES = [
    "cinematic lighting, 8k, hyperrealistic",
    "mystical, glowing runes, dark background, ethereal",
    "oil painting style, masterpiece, intricate details",
    "digital art, fantasy concept art, trending on artstation",
    "cosmic nebula background, stardust, constellation lines"
]

def generate_and_download(sign, index):
    sign_dir = os.path.join(ASSET_DIR, sign)
    if not os.path.exists(sign_dir):
        os.makedirs(sign_dir)
        
    filename = f"{sign}_{index}.jpg"
    save_path = os.path.join(sign_dir, filename)
    
    if os.path.exists(save_path):
        print(f"⚡ Skipping {filename} (Exists)")
        return

    # Pick a style based on index to get variety
    style = STYLES[index % len(STYLES)]
    seed = int(time.time()) + index # Random seed
    
    prompt = f"{sign} zodiac sign, {style}, seed-{seed}"
    # Pollinations: Free AI Image Generator
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1920&nologo=true&seed={seed}"
    
    print(f"🎨 Painting {sign} #{index+1}...")
    
    print(f"   Requesting {url}...")
    try:
        response = requests.get(url, stream=True, timeout=5)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            print(f"✅ Saved: {save_path}")
        else:
            print(f"❌ Failed to generate {sign} #{index+1}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Respect the server
    time.sleep(1)

def main():
    # 1. Create Base Directory
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"📂 Created directory: {ASSET_DIR}")

    print("🚀 Starting Zodiac Asset Expansion (10 images per sign)...")
    print("This will generate 120 unique images. Please be patient.")

    for sign in SIGNS:
        print(f"\n🔮 Processing {sign}...")
        for i in range(10): # 10 images per sign
            generate_and_download(sign, i)

    print("\n🎉 All 120 Zodiac Assets Generated & Downloaded.")

if __name__ == "__main__":
    main()

