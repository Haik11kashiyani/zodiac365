import json, random, datetime, sys
from ai_engine import ask_ai

MAJORS = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]

def generate_reading(date_str):
    # Picking 3 cards from the Major Arcana loop
    indices = random.sample(range(22), 3)
    cards = [MAJORS[i] for i in indices]
    files = [f"m{i:02d}.jpg" for i in indices]
    
    prompt = f"Date: {date_str}. Cards: {cards}. Write a 60s viral mystical script in 3 acts: Hook, Reading, CTA."
    data = ask_ai(prompt, "Output valid JSON only.")
    if not data: sys.exit(1)
    
    data.update({"card_images": files, "file_name": f"final_tarot_{date_str}.mp4"})
    with open(f"plan_tarot_{date_str}.json", "w") as f: json.dump(data, f, indent=4)

if __name__ == "__main__": generate_reading(str(datetime.date.today()))
