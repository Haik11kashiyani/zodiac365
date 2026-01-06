import json, sys, os, datetime
from ai_engine import ask_ai

# Force UTF-8 for Windows Consoles
sys.stdout.reconfigure(encoding='utf-8')

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
    elif mode == 'weekly':
        prompt = prompts.get("weekly", prompts.get("daily")).format(sign=target, date=date_str)
        imgs = [f"assets/zodiac_signs/{target}.jpg"]
    else:
        # Default Daily/Monthly
        prompt_template = prompts.get(mode, prompts.get("daily"))
        prompt = prompt_template.format(sign=target, date=date_str)
        imgs = [f"assets/zodiac_signs/{target}.jpg"]

    today_context = datetime.date.today().strftime("%B %d, %Y")
    
    prompt_suffix = f"""
    
    CONTEXT: Today is {today_context}. Use this to find trending keywords if relevant.
    
    Respond in JSON ONLY with the following keys:
    - 'script_text': The spoken word script (approx 40-50 secs). Engaging, mystical, direct.
    - 'title': Internal title.
    - 'youtube_title': A viral, click-bait style YouTube Short title (max 80 chars). MUST INCLUDE '#shorts'.
    - 'youtube_description': A 3-line engaging description with questions to drive comments. Include 3-4 hashtags in the text.
    - 'youtube_tags': A list of 15-20 high volume viral tags. Mix broad (e.g., #astrology) and specific/trending (e.g., #manifestation, #{target}).
    
    STRICT RULES:
    1. 'youtube_title' MUST end with #shorts
    2. Make it CLICKBAIT. High emotion.
    """
    
    data = ask_ai(prompt + prompt_suffix)
    if not data: return None
    
    # ENFORCE #SHORTS
    if 'youtube_title' in data:
        if '#shorts' not in data['youtube_title'].lower():
            data['youtube_title'] += " #shorts"
    
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
