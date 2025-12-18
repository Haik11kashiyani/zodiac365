import json, os
from ai_engine import ask_ai

def polish(plan_file):
    print(f"🎬 Directing {plan_file}...")
    with open(plan_file, 'r') as f: draft = json.load(f)
    
    prompt = f"""
    Optimize for Viral Retention. 
    Script: {draft.get('script_text', '')}
    
    RULES:
    1. Start with an urgent Hook.
    2. Mention 'thezodiacvault.kesug.com' as the place for personal readings.
    3. Output 3 dynamic text 'overlays' for the screen.
    
    JSON keys: 'script_text', 'title', 'overlays' (list of {{'text': '', 'time': 'start/middle/end'}})
    """
    new_data = ask_ai(prompt)
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)

if __name__ == "__main__":
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]: polish(f)
