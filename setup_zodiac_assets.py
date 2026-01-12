import os
import requests
import time
import shutil
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# SEMANTIC THEMES for context-aware fallbacks
THEMES = {
    "Love": "romantic atmosphere, glowing red hearts, soft pink lighting, emotional connection, roses",
    "Career": "wealth, gold coins, luxurious office, success, stack of money, business growth, golden glow",
    "Health": "vitality, nature, meditating, green glowing aura, healing energy, organic, peaceful forest",
    "Travel": "adventure, majestic mountains, vintage world map, compass, airplane, scenic view, wanderlust"
}

def generate_and_download_variant(sign, suffix, prompt_detail):
    sign_dir = os.path.join(ASSET_DIR, sign)
    if not os.path.exists(sign_dir):
        os.makedirs(sign_dir)
        
    filename = f"{sign}_{suffix}.jpg"
    save_path = os.path.join(sign_dir, filename)
    
    if os.path.exists(save_path):
        print(f"⚡ Skipping {filename} (Exists)")
        return

    # Construct Prompt
    # e.g. "Aries zodiac sign, romantic atmosphere..., 8k, hyperrealistic"
    full_prompt = f"{sign} zodiac sign, {prompt_detail}, 8k, hyperrealistic, masterpiece"
    seed = int(time.time()) + len(suffix) # Random seed variant
    
    url = f"https://image.pollinations.ai/prompt/{full_prompt}?width=1080&height=1920&nologo=true&seed={seed}"
    
    print(f"🎨 Painting {sign} [{suffix}]...")
    print(f"   Requesting {url}...")
    
    # Retry logic
    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(3):
        try:
            # Disable SSL verify because this free API triggers occasional weird SSL errors
            response = requests.get(url, stream=True, timeout=60, headers=headers, verify=False)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                print(f"✅ Saved: {save_path}")
                return # Success
            else:
                print(f"   Attempt {attempt+1}: Status {response.status_code}")
        except Exception as e:
            print(f"   Attempt {attempt+1} Error: {e}")
        
        time.sleep(2)
        
    print(f"❌ Failed to generate {sign} [{suffix}]")


def generate_and_download(sign, index):
    # Wrapper for old numbered style
    style = STYLES[index % len(STYLES)]
    seed = int(time.time()) + index
    prompt = f"{style}, seed-{seed}"
    generate_and_download_variant(sign, str(index), prompt)

        
    # Respect the server
    time.sleep(1)

def organize_legacy_assets():
    """Moves old single files (Aries.jpg) into their new folders (Aries/Aries_legacy.jpg)"""
    print("\n🧹 Organizing legacy assets...")
    for sign in SIGNS:
        legacy_file = os.path.join(ASSET_DIR, f"{sign}.jpg")
        sign_dir = os.path.join(ASSET_DIR, sign)
        
        if not os.path.exists(sign_dir):
            os.makedirs(sign_dir)
            
        if os.path.exists(legacy_file):
            new_path = os.path.join(sign_dir, f"{sign}_legacy.jpg")
            if not os.path.exists(new_path):
                print(f"📦 Moving {legacy_file} -> {new_path}")
                shutil.move(legacy_file, new_path)
            else:
                print(f"⚠️  Legacy file already exists in folder, removing duplicate: {legacy_file}")
                os.remove(legacy_file)
    print("✨ Cleanup complete.\n")

def main():
    # 1. Create Base Directory
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR)
        print(f"📂 Created directory: {ASSET_DIR}")
        
    # 2. Cleanup Old Files
    organize_legacy_assets()

    print("🚀 Starting Zodiac Asset Expansion (10 images per sign)...")
    print("This will generate 120 unique images. Please be patient.")

    for sign in SIGNS:
        print(f"\n🔮 Processing {sign}...")
        for i in range(10): # 10 images per sign
            generate_and_download(sign, i)
            
        # Themed Generation
        for theme_name, theme_prompt in THEMES.items():
            generate_and_download_variant(sign, theme_name, theme_prompt)

    print("\n🎉 All 120 Zodiac Assets Generated & Downloaded.")

if __name__ == "__main__":
    main()

