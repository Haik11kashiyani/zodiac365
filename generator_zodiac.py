import json, sys, os
from ai_engine import ask_ai

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def generate_content(mode, target, date_str):
    """Pure logic to generate content and return dict."""
    print(f"🔮 Drafting {mode.upper()} for {target}...")
    config = load_config()
    prompts = config.get("prompts", {})
    imgs = []

    if mode == 'compatibility':
        s1, s2 = target.split(' vs ')
        imgs = [f"assets/zodiac_signs/{s1}.jpg", f"assets/zodiac_signs/{s2}.jpg"]
        prompt = prompts.get("compatibility", "").format(sign1=s1, sign2=s2)
    elif mode == 'special':
        # The wild card
        prompt = prompts.get("special", "").format(topic=target)
        imgs = [] 
    elif mode == 'birthday':
        prompt = prompts.get("birthday", "").format(sign=target, date=date_str)
        imgs = [f"assets/zodiac_signs/{target}.jpg"]
    elif mode == 'yearly':
        prompt = prompts.get("yearly", "").format(sign=target)
        imgs = [f"assets/zodiac_signs/{target}.jpg"]
    else:
        # Default Daily/Monthly
        prompt_template = prompts.get(mode, prompts.get("daily"))
        prompt = prompt_template.format(sign=target, date=date_str)
        imgs = [f"assets/zodiac_signs/{target}.jpg"]

    data = ask_ai(prompt + " JSON ONLY with 'script_text' and 'title'.")
    if not data: return None
    
    data.update({
        'type': mode, 
        'target': target, # Ensure target is saved
        'date': date_str, # CRITICAL FIX: Save the date!
        'images': [i for i in imgs if i], 
        'active': True,
        'status': 'pending'
    })
    return data

def generate_zodiac_video(mode, target, date_str):
    # Safe filename: replace spaces and slashes
    safe_target = target.replace(' ', '_').replace('/', '-')
    filename = f"plan_{mode}_{safe_target}.json"

    # 1. CHECK FOR MANUAL OVERRIDE (If file is pending, don't overwrite)
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f: existing = json.load(f)
            if existing.get('status') == 'pending' and existing.get('active', True):
                print(f"✋ MANUAL OVERRIDE FOUND: {filename} is pending. Skipping AI generation.")
                return True
        except: pass

    data = generate_content(mode, target, date_str)
    if not data: return False
    
    data['file_name'] = filename
    with open(filename, "w") as f: json.dump(data, f, indent=4)
    return True
