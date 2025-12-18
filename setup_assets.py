import os, requests, time, sys
from urllib.parse import quote

ASSETS = "assets"
STYLE = "modern cinematic dark fantasy art, glowing gold details, 8k resolution, vertical ratio, mystical"

def generate_image(prompt, save_dir, filename):
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    path = os.path.join(save_dir, filename)
    if os.path.exists(path) and os.path.getsize(path) > 10000: return True
    
    url = f"https://image.pollinations.ai/prompt/{quote(prompt + ', ' + STYLE)}?width=1080&height=1920&nologo=true&model=flux"
    try:
        print(f"🎨 Painting: {prompt}...")
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
        if r.status_code == 200:
            with open(path, 'wb') as f: f.write(r.content)
            time.sleep(2)
            return True
    except: return False

def main():
    # Tarot
    for i, n in enumerate(["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]):
        generate_image(f"Tarot {n}", os.path.join(ASSETS, "tarot_cards"), f"m{i:02d}.jpg")
    # Zodiac
    for s in ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]:
        generate_image(f"Zodiac {s} God", os.path.join(ASSETS, "zodiac_signs"), f"{s}.jpg")

if __name__ == "__main__": main()
