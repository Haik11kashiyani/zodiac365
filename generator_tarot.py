import json
import random
import datetime
import sys
from ai_engine import ask_ai

# Map Card Names to File Names (Must match setup_assets.py)
TAROT_DECK = {}
# Major Arcana
majors = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]
for i, name in enumerate(majors): TAROT_DECK[name] = f"m{i:02d}.jpg"
# Minor Arcana (Simple mapping for now)
suits = {"Wands": "w", "Cups": "c", "Swords": "s", "Pentacles": "p"}
for s_name, s_code in suits.items():
    TAROT_DECK[f"Ace of {s_name}"] = f"{s_code}01.jpg"
    TAROT_DECK[f"Two of {s_name}"] = f"{s_code}02.jpg"
    # ... (Logic implies random selection works from keys)

def generate_reading(date_str):
    print(f"🔮 Generating Plan for {date_str}...")
    
    # Pick 3 Random Cards
    keys = list(TAROT_DECK.keys())
    # Add some minors manually to list if needed, or just stick to Majors for safety
    # For this full code, let's just use Majors + Aces to ensure files exist
    cards = random.sample(keys, 3)
    files = [TAROT_DECK[c] for c in cards]
    
    prompt = f"""
    You are a Mystic. Date: {date_str}.
    Cards: {cards[0]}, {cards[1]}, {cards[2]}.
    
    Write a 60s YouTube Short Script.
    OUTPUT JSON ONLY:
    {{
        "title": "UPPERCASE CLICKBAIT TITLE",
        "script_text": "Hook... Body... CTA...",
        "visual_notes": "Dark mood"
    }}
    """
    
    data = ask_ai(prompt, "Return valid JSON.")
    if not data: sys.exit(1)
    
    data["type"] = "TAROT"
    data["file_name"] = f"final_tarot_{date_str}.mp4"
    data["card_images"] = files
    data["card_names"] = cards
    
    with open(f"plan_tarot_{date_str}.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✅ Plan Generated.")

if __name__ == "__main__":
    generate_reading(str(datetime.date.today()))
