import json
import random
import datetime
import sys
from ai_engine import ask_ai

# Use Major Arcana only for guaranteed high-quality renders
TAROT_DECK = {
    "The Fool": "m00.jpg", "The Magician": "m01.jpg", "The High Priestess": "m02.jpg",
    "The Empress": "m03.jpg", "The Emperor": "m04.jpg", "The Hierophant": "m05.jpg",
    "The Lovers": "m06.jpg", "The Chariot": "m07.jpg", "Strength": "m08.jpg",
    "The Hermit": "m09.jpg", "Wheel of Fortune": "m10.jpg", "Justice": "m11.jpg",
    "The Hanged Man": "m12.jpg", "Death": "m13.jpg", "Temperance": "m14.jpg",
    "The Devil": "m15.jpg", "The Tower": "m16.jpg", "The Star": "m17.jpg",
    "The Moon": "m18.jpg", "The Sun": "m19.jpg", "Judgement": "m20.jpg",
    "The World": "m21.jpg"
}

def generate_reading(date_str):
    print(f"🔮 Generating Plan for {date_str}...")
    selected_names = random.sample(list(TAROT_DECK.keys()), 3)
    selected_files = [TAROT_DECK[name] for name in selected_names]
    
    prompt = f"Date: {date_str}. Cards: {selected_names}. Write a 60s viral mystical script."
    data = ask_ai(prompt, "Output JSON ONLY.")
    
    if data:
        data["card_images"] = selected_files
        data["file_name"] = f"final_tarot_{date_str}.mp4"
        with open(f"plan_tarot_{date_str}.json", "w") as f:
            json.dump(data, f)
        print("✅ Plan Ready.")

if __name__ == "__main__":
    generate_reading(str(datetime.date.today()))
