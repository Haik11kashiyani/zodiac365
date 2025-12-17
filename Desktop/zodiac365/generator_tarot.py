import os
import json
import random
import datetime
from ai_engine import ask_ai

# --- CONFIGURATION ---
# Full 78 Card Mapping (Name -> Filename)
# m=Major, w=Wands, c=Cups, s=Swords, p=Pentacles
TAROT_DECK = {
    # MAJOR ARCANA
    "The Fool": "m00.jpg", "The Magician": "m01.jpg", "The High Priestess": "m02.jpg",
    "The Empress": "m03.jpg", "The Emperor": "m04.jpg", "The Hierophant": "m05.jpg",
    "The Lovers": "m06.jpg", "The Chariot": "m07.jpg", "Strength": "m08.jpg",
    "The Hermit": "m09.jpg", "Wheel of Fortune": "m10.jpg", "Justice": "m11.jpg",
    "The Hanged Man": "m12.jpg", "Death": "m13.jpg", "Temperance": "m14.jpg",
    "The Devil": "m15.jpg", "The Tower": "m16.jpg", "The Star": "m17.jpg",
    "The Moon": "m18.jpg", "The Sun": "m19.jpg", "Judgement": "m20.jpg", "The World": "m21.jpg",

    # WANDS (Fire - Passion, Action)
    "Ace of Wands": "w01.jpg", "Two of Wands": "w02.jpg", "Three of Wands": "w03.jpg",
    "Four of Wands": "w04.jpg", "Five of Wands": "w05.jpg", "Six of Wands": "w06.jpg",
    "Seven of Wands": "w07.jpg", "Eight of Wands": "w08.jpg", "Nine of Wands": "w09.jpg",
    "Ten of Wands": "w10.jpg", "Page of Wands": "w11.jpg", "Knight of Wands": "w12.jpg",
    "Queen of Wands": "w13.jpg", "King of Wands": "w14.jpg",

    # CUPS (Water - Emotions, Love)
    "Ace of Cups": "c01.jpg", "Two of Cups": "c02.jpg", "Three of Cups": "c03.jpg",
    "Four of Cups": "c04.jpg", "Five of Cups": "c05.jpg", "Six of Cups": "c06.jpg",
    "Seven of Cups": "c07.jpg", "Eight of Cups": "c08.jpg", "Nine of Cups": "c09.jpg",
    "Ten of Cups": "c10.jpg", "Page of Cups": "c11.jpg", "Knight of Cups": "c12.jpg",
    "Queen of Cups": "c13.jpg", "King of Cups": "c14.jpg",

    # SWORDS (Air - Intellect, Conflict)
    "Ace of Swords": "s01.jpg", "Two of Swords": "s02.jpg", "Three of Swords": "s03.jpg",
    "Four of Swords": "s04.jpg", "Five of Swords": "s05.jpg", "Six of Swords": "s06.jpg",
    "Seven of Swords": "s07.jpg", "Eight of Swords": "s08.jpg", "Nine of Swords": "s09.jpg",
    "Ten of Swords": "s10.jpg", "Page of Swords": "s11.jpg", "Knight of Swords": "s12.jpg",
    "Queen of Swords": "s13.jpg", "King of Swords": "s14.jpg",

    # PENTACLES (Earth - Money, Career)
    "Ace of Pentacles": "p01.jpg", "Two of Pentacles": "p02.jpg", "Three of Pentacles": "p03.jpg",
    "Four of Pentacles": "p04.jpg", "Five of Pentacles": "p05.jpg", "Six of Pentacles": "p06.jpg",
    "Seven of Pentacles": "p07.jpg", "Eight of Pentacles": "p08.jpg", "Nine of Pentacles": "p09.jpg",
    "Ten of Pentacles": "p10.jpg", "Page of Pentacles": "p11.jpg", "Knight of Pentacles": "p12.jpg",
    "Queen of Pentacles": "p13.jpg", "King of Pentacles": "p14.jpg"
}

def generate_tarot_reading(date_str):
    print(f"🔮 Picking cards for {date_str}...")
    
    # 1. Pick 3 Random Cards (Keys)
    all_card_names = list(TAROT_DECK.keys())
    selected_names = random.sample(all_card_names, 3)
    
    card_1_name = selected_names[0]
    card_2_name = selected_names[1]
    card_3_name = selected_names[2]

    # Get filenames for the Video Maker
    card_1_file = TAROT_DECK[card_1_name]
    card_2_file = TAROT_DECK[card_2_name]
    card_3_file = TAROT_DECK[card_3_name]
    
    print(f"🎴 Cards Drawn: {card_1_name}, {card_2_name}, {card_3_name}")
    
    # 2. Construct the Prompt for AI
    prompt = f"""
    You are a mystical Tarot Reader. Today is {date_str}.
    I have drawn three cards for the collective audience:
    1. {card_1_name} (The Situation)
    2. {card_2_name} (The Challenge)
    3. {card_3_name} (The Outcome)
    
    Task: Write a viral 60-second YouTube Shorts script.
    
    RULES:
    - Hook (0-5s): "Stop scrolling! Your message for today is..."
    - Middle (5-45s): Interpret the combination of {card_1_name}, {card_2_name}, and {card_3_name}. Focus on 'love' or 'money'. Be specific.
    - End (45-60s): Call to Action. "To claim this energy, comment 'So Mote It Be' and subscribe."
    - Tone: Mystical, Urgent, Empowering.
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "title": "Pick a Card 🔮 {date_str} (Don't Ignore This!)",
        "script_text": "Stop scrolling... [Full Script Here]",
        "description": "Daily Tarot Reading for {date_str}. \\n\\nCards: {card_1_name}, {card_2_name}, {card_3_name}. \\n\\n#tarot #manifestation #shorts #zodiac",
        "tags": ["tarot", "pickacard", "dailyreading", "astrology", "witchtok"],
        "visual_notes": "Dark aesthetic, mystical background"
    }}
    """
    
    # 3. Get AI Response
    video_data = ask_ai(prompt, system_instruction="You are a mystic. Speak with authority and mystery.")
    
    if video_data:
        # 4. Add technical data for the Video Maker
        filename = f"plan_tarot_{date_str}.json"
        
        video_data["type"] = "TAROT"
        video_data["date"] = date_str
        video_data["file_name"] = f"final_tarot_{date_str}.mp4"
        
        # IMPORTANT: Pass the exact filenames to the video maker
        video_data["card_images"] = [card_1_file, card_2_file, card_3_file]
        video_data["card_names"] = [card_1_name, card_2_name, card_3_name]
        
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(video_data, f, indent=4)
            
        print(f"✅ Tarot Plan Saved: {filename}")
        return filename
    else:
        print("❌ Failed to generate Tarot reading.")
        return None

if __name__ == "__main__":
    today = datetime.datetime.now().date()
    generate_tarot_reading(str(today))