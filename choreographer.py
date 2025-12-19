import json, os
from ai_engine import ask_ai

def polish(plan_file):
    with open(plan_file, 'r') as f: draft = json.load(f)
    print(f"🎬 GOD-MODE DIRECTING: {plan_file}...")
    
    prompt = f"""
    You are a World-Class Documentary & Viral Director. 
    Refine this script for a deep, mystical, human experience.
    
    Original Content: {draft.get('script_text', '')}
    Type: {draft.get('type', 'astrology')}
    
    DIRECTOR'S REQUIREMENTS:
    1. REMOVE ALL HASHTAGS, ASTERISKS, AND EMOJIS. Pure spoken words only.
    2. HOOK: Start with a heavy, atmospheric question.
    3. CTA: Weave 'thezodiacvault.kesug.com' into the story naturally (e.g., 'Your full path is waiting at...').
    4. PACING: Use commas and periods to create natural pauses for the voice.
    
    OUTPUT JSON ONLY:
    {{
        "title": "A Punchy Catchy Title No Punctuation",
        "script_text": "The refined, spoken-only masterpiece..."
    }}
    """
    new_data = ask_ai(prompt, sys_msg="You are a high-end cinematic content director.")
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)

if __name__ == "__main__":
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]: polish(f)
