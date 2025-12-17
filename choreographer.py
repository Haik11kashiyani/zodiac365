import json
import os
import sys
from ai_engine import ask_ai

def polish_script(plan_file):
    print(f"🧐 Choreographer is reviewing: {plan_file}")
    
    # 1. READ THE DRAFT
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            draft = json.load(f)
    except Exception as e:
        print(f"❌ Error reading plan file: {e}")
        return

    # 2. THE DIRECTOR'S PROMPT
    prompt = f"""
    You are a Master Viral Video Director for YouTube Shorts.
    Reword this script to be 'Dark, Mystical, and Urgent'.
    
    CURRENT DRAFT:
    Title: {draft['title']}
    Script: {draft['script_text']}
    
    INSTRUCTIONS:
    1. Output strictly JSON.
    2. HOOK: Rewrite the first sentence to be a scroll-stopper.
    3. ENDING: Add a CTA "Comment So Mote It Be".
    4. TITLE: Clickbait title, UPPERCASE.
    
    OUTPUT FORMAT:
    ```json
    {{
        "title": "NEW TITLE",
        "script_text": "New script...",
        "visual_notes": "Mood notes"
    }}
    ```
    """
    
    print("🎬 Polishing script with AI Director...")
    # System instruction emphasizes JSON to help the simpler models
    polished_data = ask_ai(prompt, system_instruction="You are a Viral Editor. You respond ONLY in valid JSON.")
    
    if polished_data:
        print(f"✨ Original Title: {draft['title']}")
        print(f"🚀 New Viral Title: {polished_data.get('title', 'NO TITLE')}")
        
        # Update draft safely
        draft['title'] = polished_data.get('title', draft['title'])
        draft['script_text'] = polished_data.get('script_text', draft['script_text'])
        draft['choreography_notes'] = polished_data.get('visual_notes', '')
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(draft, f, indent=4)
            
        print("✅ Script updated successfully.")
    else:
        print("⚠️ Choreographer failed (AI Error). Keeping original draft.")

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot') and f.endswith('.json')]
    if files:
        latest = max(files, key=os.path.getctime)
        polish_script(latest)
    else:
        print("❌ No plan file found.")
