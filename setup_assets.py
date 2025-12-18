import os, requests, time, sys
from urllib.parse import quote

ASSET_DIR = "assets/tarot_cards"
BASE_URL = "https://image.pollinations.ai/prompt/"
STYLE = "modern cinematic tarot card, dark fantasy art, 8k resolution, glowing intricate details, vertical ratio"

def generate_image(prompt, filename):
    save_path = os.path.join(ASSET_DIR, filename)
    if os.path.exists(save_path) and os.path.getsize(save_path) > 10000: return True
    full_prompt = quote(f"{prompt}, {STYLE}")
    url = f"{BASE_URL}{full_prompt}?width=1080&height=1920&nologo=true&model=flux"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
        if r.status_code == 200:
            with open(save_path, 'wb') as f: f.write(r.content)
            time.sleep(2)
            return True
    except: return False

def main():
    if not os.path.exists(ASSET_DIR): os.makedirs(ASSET_DIR)
    cards = []
    majors = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]
    for i, name in enumerate(majors): cards.append((name, f"m{i:02d}.jpg"))
    for s_name, s_code in {"Wands":"w", "Cups":"c", "Swords":"s", "Pentacles":"p"}.items():
        for i, r_name in enumerate(["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]):
            cards.append((f"{r_name} of {s_name}", f"{s_code}{i+1:02d}.jpg"))
    success = 0
    for name, filename in cards:
        if generate_image(name, filename): success += 1
    if success < 60: sys.exit(1)

if __name__ == "__main__": main()
