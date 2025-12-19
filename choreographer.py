import json, os
from ai_engine import ask_ai

def polish(plan_file):
    with open(plan_file, 'r') as f: draft = json.load(f)
    print(f"🎬 MASTER DIRECTING: {plan_file}...")
    
    prompt = f"""
    You are a viral YouTube Shorts director. 
    Rewrite this {draft.get('type', 'astrology')} script for MAXIMUM RETENTION.
    
    Original: {draft.get('script_text', '')}
    
    INSTRUCTIONS:
    1. The first sentence MUST be a shocking pattern interrupt.
    2. TITLE: Create a catchy title WITHOUT using colons (:), question marks (?), or slashes (/).
    3. Use urgent, fast-paced language.
    
    OUTPUT JSON ONLY with keys 'script_text' and 'title'.
    """
    new_data = ask_ai(prompt, sys_msg="You are a viral content director.")
    if new_data:
        draft.update(new_data)
        with open(plan_file, 'w') as f: json.dump(draft, f, indent=4)

if __name__ == "__main__":
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]:
        polish(f)
