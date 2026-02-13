import json, sys, os, datetime
from ai_engine import ask_ai

# Force UTF-8 for Windows Consoles
sys.stdout.reconfigure(encoding='utf-8')

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def generate_content(mode, target, date_str):
    """Pure logic to generate content and return dict."""
    print(f"» Drafting {mode.upper()} for {target}...")
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
    
    # VTT and REMOTION BRIDGE
    prompt_suffix = f"""
    CONTEXT: Today is {today_context}.
    
    Respond in JSON ONLY:
    {{
        "script_text": "Spoken script ~50s. START WITH A STOP WORD (Wait, Stop, Listen). High energy.",
        "captions_structure": [
            {{"text": "LEO WARNING", "type": "header"}},
            {{"text": "Stop scrolling...", "type": "normal"}}
        ],
        "lucky_numbers": ["7", "11", "21"],
        "lucky_color": "Emerald Green",
        "monthly_vibe": "Reflective & Calm",
        "title": "Internal Title",
        "youtube_title": "⚠️ WARNING: [Sign]... #shorts", 
        "youtube_description": "First line must be a hook! Include 5+ tags.",
        "youtube_tags": ["tag1", "tag2"]
    }}
    
    VIRAL RULES (200% VIRALITY):
    1. **TITLE**: Must be CLICKBAIT. Use "⚠️", "🔮", "Don't Ignore", "Urgent". Max 50 chars.
    2. **SCRIPT**: Start with a PATTERN INTERRUPT ("Stop scrolling!", "You need to hear this!").
    3. **DESCRIPTION**: Line 1 is the HOOK. Include "Sub to claim" CTA.
    4. **TAGS**: Generate 20 high-volume tags mixing Broad (#astrology) + Niche (#{target.lower()}).
    5. **EXTRAS**:
       - lucky_numbers: 3 distinct lucky numbers.
       - lucky_color: A specific, evocative color (e.g. "Royal Blue", "Sunset Orange").
       - monthly_vibe: 2-3 words describing the core theme (e.g. "Bold Action", "Quiet Reflection").
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
        'lucky_numbers': data.get('lucky_numbers', []),
        'lucky_color': data.get('lucky_color', ''),
        'monthly_vibe': data.get('monthly_vibe', ''),
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
                print(f"ℹ️ MANUAL OVERRIDE FOUND: {filename} is pending. Skipping AI generation.")
                return True
        except: pass

    data = generate_content(mode, target, date_str)
    if not data: return False
    
    data['file_name'] = filename
    with open(filename, "w") as f: json.dump(data, f, indent=4)
    return True
