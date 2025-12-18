import json, sys, os
from ai_engine import ask_ai

def generate_zodiac_video(mode, target, date_str):
    print(f"🔮 Drafting {mode.upper()} for {target}...")
    imgs = [f"assets/zodiac_signs/{target}.jpg"]
    
    if mode == 'compatibility':
        s1, s2 = target.split(' vs ')
        imgs = [f"assets/zodiac_signs/{s1}.jpg", f"assets/zodiac_signs/{s2}.jpg"]
        prompt = f"Viral compatibility script for {s1} and {s2}. Cover Love and Trust."
    elif mode == 'birthday':
        prompt = f"Viral personality secrets for people born on {target}. Use Numerology."
        imgs = [] 
    elif mode == 'archetype': # NEW UNRESTRICTED MODE
        prompt = f"Write a 'Dark Psychology' script about {target}. Focus on their hidden 'Shadow Side' and why people fear them. Make it viral and mysterious."
    else:
        prompt = f"Viral {mode} prediction for {target} for {date_str}. Dark tone."

    data = ask_ai(prompt + " JSON ONLY with 'script_text' and 'title'.")
    if not data: return False
    
    data.update({'type': mode, 'images': imgs, 'file_name': f"plan_{mode}_{target.replace(' ', '_')}.json"})
    with open(data['file_name'], "w") as f: json.dump(data, f, indent=4)
    return True
