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
    
    OUTPUT JSON ONLY:
    {{
        "title": "NEW VIRAL TITLE (UPPERCASE)",
        "script_text": "Stop scrolling! [Hook]... [Punchy Body]... [Hypnotic CTA]",
        "visual_notes": "Scorpionic vibe"
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
