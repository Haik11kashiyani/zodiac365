import json, os
from ai_engine import ask_ai

def polish(plan_file):
    with open(plan_file, 'r') as f: draft = json.load(f)
    
    prompt = f"""Optimize for Viral Retention. Script: {draft.get('script_text', '')}
    MANDATORY: Mention 'thezodiacvault.kesug.com' or 'link in bio' for personal readings.
    Output 3 dynamic text 'overlays' (Max 3 words each) at 'start', 'middle', 'end'.
    JSON keys: 'script_text', 'title', 'overlays' (list of {{'text': '', 'time': ''}})"""
    
    new_data = ask_ai(prompt)
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)

if __name__ == "__main__":
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]: polish(f)
