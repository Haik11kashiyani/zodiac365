import json
import os
from ai_engine import ask_ai

def polish(plan_file):
    print(f"🎬 Polishing {plan_file}...")
    with open(plan_file, 'r') as f: draft = json.load(f)
    
    prompt = f"""
    Rewrite this YouTube Shorts script to be VIRAL, DARK, and URGENT.
    Title: {draft['title']}
    Script: {draft['script_text']}
    
    MANDATORY:
    1. Start with a "Stop Scrolling" Hook.
    2. End with a spoken CTA: "To claim this energy, comment So Mote It Be."
    3. Generate 3 short Text Overlays (Max 3 words).
    
    OUTPUT JSON ONLY:
    {{
        "title": "NEW VIRAL TITLE (UPPERCASE)",
        "script_text": "Stop scrolling! [Hook]... [Body]... To claim this energy, comment So Mote It Be.",
        "overlays": [
            {{"text": "DON'T IGNORE", "time": "start"}},
            {{"text": "BIG CHANGE COMING", "time": "middle"}},
            {{"text": "CLAIM NOW", "time": "end"}}
        ]
    }}
    """
    new_data = ask_ai(prompt, "Return valid JSON.")
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)
        print("✨ Script Polished.")

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot')]
    if files: polish(max(files, key=os.path.getctime))
