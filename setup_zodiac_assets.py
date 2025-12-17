import os
import requests
import time
import shutil

# --- CONFIGURATION ---
ASSET_DIR = "assets/zodiac_signs"
THEME = "mystical dark golden astrology zodiac sign, cinematic lighting, 8k, hyperrealistic"

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def generate_and_download(sign, filename, is_dark_side=False):
    # Construct a Prompt for the Free AI
    if is_dark_side:
        prompt = f"scary evil dark {sign} zodiac sign, horror theme, red eyes, smoke, 8k wallpaper"
        save_path = os.path.join(ASSET_DIR, f"{filename}_dark.jpg")
    else:
        prompt = f"{THEME} {sign} symbol, majesty, epic composition"
        save_path = os.path.join(ASSET_DIR, f"{filename}.jpg")
    
    # Pollinations.ai URL (Free, No Key Needed)
    # We encode the prompt into the URL
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1920&nologo=true"
    
    if os.path.exists(save_path):
        print(f"⚡ Skipping {save_path} (Exists)")
        return

    print(f"🎨 Painting {sign} ({'Dark' if is_dark_side else 'Normal'})...")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            print(f"✅ Saved: {save_path}")
        else:
            print(f"❌ Failed to generate {sign}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Respect the server
    time.sleep(2)

def main():
    # 1. Create Directory
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"📂 Created directory: {ASSET_DIR}")

    print("🚀 Starting Zodiac Art Generation...")

    for sign in SIGNS:
        # Generate Standard Image (For Predictions/Compatibility)
        generate_and_download(sign, sign, is_dark_side=False)
        
        # Generate Dark Side Image (For Phase 3: Dark Truths)
        generate_and_download(sign, sign, is_dark_side=True)

    print("\n🎉 All 24 Zodiac Assets Generated & Downloaded.")
    print("👉 Now commit and push the 'assets' folder to GitHub.")

if __name__ == "__main__":
    main()
