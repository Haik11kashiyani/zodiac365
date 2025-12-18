import json, sys, os
from ai_engine import ask_ai

def generate_zodiac_video(mode, target, date_str):
    print(f"🔮 Drafting {mode.upper()} for {target}...")
    imgs = []
    if mode == 'compatibility':
        s1, s2 = target.split(' vs ')
        imgs = [f"assets/zodiac_signs/{s1}.jpg", f"assets/zodiac_signs/{s2}.jpg"]
        prompt = f"Viral compatibility script for {s1} and {s2}. Cover Love and Secrets."
    elif mode == 'special':
        # NEW: The Wildcard Logic
        prompt = f"Generate a viral 1-minute occult secret video about {target} (e.g. Mercury Retrograde, Crystal Healing, or Moon Phase)."
        imgs = [] # Will use default mystical background
    else:
        imgs = [f"assets/zodiac_signs/{target}.jpg" if mode != 'birthday' else ""]
        prompt = f"Viral {mode} prediction/secret for {target}."

    data = ask_ai(prompt + " JSON ONLY with 'script_text' and 'title'.")
    if not data: return False
    
    data.update({'type': mode, 'images': [i for i in imgs if i], 'file_name': f"plan_{mode}_{target.replace(' ', '_')}.json"})
    with open(data['file_name'], "w") as f: json.dump(data, f, indent=4)
    return True
