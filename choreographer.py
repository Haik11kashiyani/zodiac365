import json, os
from ai_engine import ask_ai

def polish(plan_file):
    print(f"🎬 MASTER DIRECTOR AT WORK: {plan_file}...")
    with open(plan_file, 'r') as f: draft = json.load(f)
    
    # We provide the AI with a 'Director's Persona' to ensure high-end results
    prompt = f"""
    You are an Award-Winning Short-Form Video Director. 
    Transform this basic script into a CINEMATIC MASTERPIECE.
    
    Original Script: {draft.get('script_text', '')}
    Video Type: {draft.get('type', 'zodiac')}
    
    DIRECTOR'S RULES:
    1. HOOK: The first 3 seconds must be a 'pattern interrupt' (e.g., 'Stop! The stars just shifted.').
    2. PACING: Use short, punchy sentences for high retention.
    3. CALL TO ACTION: Naturally weave in 'thezodiacvault.kesug.com' as the solution to their destiny.
    4. VISUAL CUES: Define 5 'Visual Beats'. Each beat must have 'text' (Max 3 words) and 'effect' (zoom, shake, or fade).
    
    OUTPUT JSON ONLY:
    {{
        "title": "ULTIMATE VIRAL TITLE",
        "script_text": "The full polished script here...",
        "beats": [
            {{"text": "URGENT MESSAGE", "time": 0.5, "effect": "zoom"}},
            {{"text": "DESTINY CALLS", "time": 4.0, "effect": "fade"}},
            {{"text": "DON'T IGNORE", "time": 8.5, "effect": "shake"}},
            {{"text": "CLAIM NOW", "time": 12.0, "effect": "zoom"}},
            {{"text": "LINK IN BIO", "time": 16.0, "effect": "fade"}}
        ]
    }}
    """
    
    # Using the high-intelligence models for the Director role
    new_data = ask_ai(prompt, sys_msg="You are a professional video choreographer and viral content director.")
    
    if new_data:
        # We replace the old 'overlays' with the more advanced 'beats'
        draft.update(new_data)
        with open(plan_file, 'w') as f:
            json.dump(draft, f, indent=4)
        print("✨ Choreography complete. Director's cues added.")

if __name__ == "__main__":
    # This automatically finds every plan (Tarot, Zodiac, Birthday, Wildcard) and directs them
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]:
        polish(f)
