import json
import os

files = [
    "examples/plan_daily_all_12.json",
    "examples/plan_monthly_all_12.json",
    "examples/plan_yearly_all_12.json", 
    "examples/plan_birthday_all.json",
    "examples/plan_compatibility_all.json"
]

for fpath in files:
    if not os.path.exists(fpath): continue
    
    print(f"Resetting {fpath}...")
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not isinstance(data, list): data = [data]
    
    for item in data:
        item['script_text'] = "" # Force Regenerate
        item['status'] = "pending"
        item['uploaded'] = False
        item['active'] = True
        
        # Date Logic
        if item.get('type') == 'daily':
            item['date'] = "TODAY"
        elif item.get('type') == 'monthly':
            item['date'] = "January 2026"
        elif item.get('type') == 'yearly':
            item['date'] = "2026"
            
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
print("✅ All JSONs reset for fresh generation.")
