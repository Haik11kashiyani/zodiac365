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
    You are a Master Viral Video Director for YouTube Shorts (Zodiac/Tarot Niche).
    I have a draft script. It is too boring. I need you to "Spike the Dopamine".
    
    CURRENT DRAFT:
    Title: {draft['title']}
    Script: {draft['script_text']}
    Cards: {draft.get('card_names', 'Unknown Cards')}
    
    YOUR TASK:
    1. HOOK (0-3s): Rewrite the first sentence. It MUST stop the scroll. Use phrases like "Stop scrolling", "The universe has a warning", "Your ex is thinking about you".
    2. BODY: Keep the meaning, but make it punchy. Short sentences. Remove fluff.
    3. ENDING: Add a 'Hypnotic CTA'. Example: "To claim this energy, tap follow and comment 'So Mote It Be'."
    4. TONE: Dark, Mystical, 8th House, Scorpionic.
    5. TITLE: Write a clickbait title in UPPERCASE (Max 6 words).
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "title": "NEW VIRAL TITLE",
        "script_text": "New viral script text...",
        "visual_notes": "Specific mood instructions"
    }}
    """
    
    print("🎬 Polishing script with AI Director...")
    polished_data = ask_ai(prompt, system_instruction="You are a Viral Content Editor. You hate boring content.")
    
    if polished_data:
        # 3. MERGE & UPDATE
        print(f"✨ Original Title: {draft['title']}")
        print(f"🚀 New Viral Title: {polished_data['title']}")
        
        # Update the draft with new creative text
        draft['title'] = polished_data['title']
        draft['script_text'] = polished_data['script_text']
        draft['choreography_notes'] = polished_data.get('visual_notes', '')
        
        # Save it back to the same file (Overwrite)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(draft, f, indent=4)
            
        print("✅ Script updated successfully.")
    else:
        print("⚠️ Choreographer failed (AI Error). Keeping original draft.")

if __name__ == "__main__":
    # Find the newest plan file
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot') and f.endswith('.json')]
    if files:
        latest = max(files, key=os.path.getctime)
        polish_script(latest)
    else:
        print("❌ No plan file found to polish.")
