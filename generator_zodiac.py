import json, sys, os, datetime
from ai_engine import ask_ai
from youtube_uploader import sanitize_youtube_tags

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
    
    # Detect actual sign name for captions (handle "X vs Y" for compatibility)
    caption_sign = target.split(' vs ')[0] if ' vs ' in target else target
    
    # VTT and REMOTION BRIDGE
    prompt_suffix = f"""
    CONTEXT: Today is {today_context}. The target sign is {target}.
    
    CRITICAL CONTENT RULES:
    - The script MUST contain REAL astrological predictions specific to {target}
    - Reference {target}'s actual RULING PLANET and ELEMENT in the script
    - Use SPECIFIC house numbers (1st House, 7th House, 10th House, etc.)
    - Use REAL planetary aspects (trine, square, opposition, conjunction, sextile)
    - Include at least ONE specific prediction about LOVE and ONE about CAREER/MONEY
    - The predictions must sound like a REAL professional astrologer, NOT generic motivation
    - NEVER use placeholder text like [Element] or [Number] — fill in the REAL values
    - The script must be a COMPLETE, spoken narration — no headers, no bullet points
    - Flow naturally as if speaking directly to the viewer
    
    Respond in JSON ONLY:
    {{
        "script_text": "The FULL spoken narration script. Must follow the structure defined in the main prompt above. 140-150 words (55-60 seconds). Start with a pattern interrupt. Include specific planetary transits, house references, love prediction, career prediction, and a closing CTA. Must be specific to {target} — never generic.",
        "captions_structure": [
            {{"text": "{caption_sign.upper()} ALERT", "type": "header"}},
            {{"text": "First line of the script...", "type": "normal"}}
        ],
        "lucky_numbers": ["7", "11", "21"],
        "lucky_color": "Emerald Green",
        "monthly_vibe": "Reflective & Calm",
        "title": "{target} {mode.title()} Horoscope {today_context}",
        "youtube_title": "Short punchy title under 50 chars, curiosity-driven, NO hashtags, NO emojis, must include {target}",
        "youtube_description": "2-3 sentence hook that creates curiosity. Personal tone as if talking directly to {target}. Include a specific teaser about what the prediction reveals.",
        "youtube_tags": ["astrology", "horoscope", "{target.lower()}", "...up to 12 short tags"]
    }}
    
    FORMAT RULES:
    1. **TITLE**: Max 50 chars. Must include "{target}". Curiosity gap style. Examples: "The Stars Are Warning {target}...", "{target} — Don't Ignore This", "Something Big Is Coming for {target}". NO hashtags. NO emojis.
    2. **SCRIPT**: MUST follow the structured sections from the main prompt. Every section must be present. No skipping.
    3. **DESCRIPTION**: 2-3 sentences that tease the specific prediction. Mention what planet or transit the video covers. Include "Comment your sign" CTA.
    4. **TAGS**: Exactly 10-12 tags. Each tag max 25 characters. Lowercase only, NO # symbols, NO brand names (tiktok, instagram). Short phrases only (e.g. "libra horoscope", "cosmic energy"). Avoid long planetary aspect strings.
    5. **CAPTIONS_STRUCTURE**: The header MUST say "{caption_sign.upper()}" — NEVER use a different sign name.
    6. **EXTRAS**:
       - lucky_numbers: 3 distinct lucky numbers between 1-99.
       - lucky_color: A specific, evocative color (e.g. "Royal Blue", "Sunset Orange").
       - monthly_vibe: 2-3 words describing the core energy theme (e.g. "Bold Action", "Deep Reflection").
    """
    
    data = ask_ai(prompt + prompt_suffix)
    if not data: return None

    # Normalize and sanitize YouTube tags at generation time (prevents upload failures)
    raw_tags = data.get('youtube_tags') or data.get('tags') or []
    if isinstance(raw_tags, list):
        data['youtube_tags'] = sanitize_youtube_tags(raw_tags)
    data.pop('tags', None)

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
