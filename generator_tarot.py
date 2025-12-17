import json
import random
import datetime
import sys
from ai_engine import ask_ai

# MAP CARD NAMES TO FILES
TAROT_DECK = {}
majors = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]
for i, name in enumerate(majors): TAROT_DECK[name] = f"m{i:02d}.jpg"

suits = {"Wands": "w", "Cups": "c", "Swords": "s", "Pentacles": "p"}
ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]

for s_name, s_code in suits.items():
    for i, r_name in enumerate(ranks):
        num = i + 1
        TAROT_DECK[f"{r_name} of {s_name}"] = f"{s_code}{num:02d}.jpg"

def generate_reading(date_str):
    print(f"🔮 Generating Plan for {date_str}...")
    
    # Pick 3 Random Cards
    card_names = random.sample(list(TAROT_DECK.keys()), 3)
    card_files = [TAROT_DECK[name] for name in card_names]
    
    prompt = f"""
    You are a Mystic. Date: {date_str}.
    Cards: {card_names[0]}, {card_names[1]}, {card_names[2]}.
    
    Write a 60s YouTube Short Script.
    OUTPUT JSON ONLY:
    {{
        "title": "UPPERCASE CLICKBAIT TITLE",
        "script_text": "Hook... Body... CTA...",
        "visual_notes": "Dark mood"
    }}
    """
    
    data = ask_ai(prompt, "Return valid JSON.")
    
    if not data:
        print("❌ AI Failed to generate script.")
        sys.exit(1)
    
    data["type"] = "TAROT"
    data["file_name"] = f"final_tarot_{date_str}.mp4"
    data["card_images"] = card_files
    data["card_names"] = card_names
    
    with open(f"plan_tarot_{date_str}.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✅ Plan Generated.")

if __name__ == "__main__":
    generate_reading(str(datetime.date.today()))
