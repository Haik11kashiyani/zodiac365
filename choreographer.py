import json, os
from ai_engine import ask_ai

def polish(plan_file):
    with open(plan_file, 'r') as f: draft = json.load(f)
    
    prompt = f"""
    You are a Viral Video Director. 
    Rewrite this script for a TikTok/Reels audience. 
    
    Original: {draft.get('script_text', '')}
    
    DIRECTOR'S REQUIREMENTS:
    1. Start with a SHOCKING HOOK. (e.g., 'STOP! The universe has a secret for you...')
    2. Use short, high-energy sentences.
    3. Include 5 specific 'Visual Beats' for the editor.
    
    OUTPUT JSON ONLY:
    {{
        "title": "ULTIMATE TITLE",
        "script_text": "Clean, high-energy script here...",
        "beats": ["BEAT 1", "BEAT 2", "BEAT 3", "BEAT 4", "BEAT 5"]
    }}
    """
    new_data = ask_ai(prompt, sys_msg="You are a viral content choreographer.")
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)

if __name__ == "__main__":
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]:
        polish(f)
