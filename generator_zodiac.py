import json, sys, os
from ai_engine import ask_ai

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def generate_zodiac_video(mode, target, date_str):
    # Mode: 'monthly', 'yearly', 'birthday', 'compatibility'
    print(f"🔮 Generating {mode.upper()} for {target}...")
    
    image_paths = []
    if mode == 'compatibility':
        sign1, sign2 = target.split(' vs ')
        image_paths = [f"assets/zodiac_signs/{sign1}.jpg", f"assets/zodiac_signs/{sign2}.jpg"]
        prompt = f"Write a viral astrological compatibility script for {sign1} vs {sign2}. 60s YouTube Short."
    elif mode == 'birthday':
        # Target is a date like 'July 14'
        # Note: For birthday, we might need a generic 'birthday' image or the sun sign of that date. 
        # For simplicity, we stick to a text overlay style or use a specific sign if calculated.
        prompt = f"Write a viral 'Born on {target}' personality secrets script. 60s YouTube Short."
        image_paths = [] # Video maker will handle no-image mode or we add a default
    else:
        # Monthly/Yearly
        image_paths = [f"assets/zodiac_signs/{target}.jpg"]
        prompt = f"Write a viral {mode} horoscope for {target} for {date_str}. 60s YouTube Short."

    prompt += " OUTPUT JSON ONLY with 'script_text' and 'title'."
    
    data = ask_ai(prompt, "Return valid JSON.")
    if not data: return False
    
    data['type'] = mode
    data['images'] = image_paths
    data['file_name'] = f"final_{mode}_{target.replace(' ', '_')}.mp4"
    
    with open(f"plan_{mode}_{target.replace(' ', '_')}.json", "w") as f:
        json.dump(data, f, indent=4)
    return True
