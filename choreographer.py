import json, os
from ai_engine import ask_ai

def polish(plan_file):
    with open(plan_file, 'r') as f: draft = json.load(f)
    # The CTA is hard-coded into the prompt to ensure consistency
    prompt = f"""Rewrite this script for maximum retention. 
    MANDATORY ENDING CTA: 'For your full personal reading, visit the link in bio or thezodiacvault.kesug.com'."""
    
    new_data = ask_ai(prompt, "Return JSON only.")
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot')]
    if files: polish(max(files, key=os.path.getctime))
