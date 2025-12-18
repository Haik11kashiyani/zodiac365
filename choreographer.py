import json, random, datetime, sys
from ai_engine import ask_ai
MAJORS = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]

def generate_reading(date_str):
    indices = random.sample(range(22), 3)
    files = [f"assets/tarot_cards/m{i:02d}.jpg" for i in indices]
    prompt = f"Date: {date_str}. Cards: {[MAJORS[i] for i in indices]}. Write 60s viral script. OUTPUT JSON with 'script_text', 'title'."
    data = ask_ai(prompt)
    if not data: return
    data.update({"type": "tarot", "images": files, "file_name": f"final_tarot_{date_str}.mp4"})
    with open(f"plan_tarot_{date_str}.json", "w") as f: json.dump(data, f, indent=4)

if __name__ == "__main__": generate_reading(str(datetime.date.today()))
