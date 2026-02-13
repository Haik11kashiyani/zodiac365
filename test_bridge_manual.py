import bridge
import os

# Target the specific file we modified
filename = "plan_daily_Libra.json"

if os.path.exists(filename):
    print(f"Processing {filename}...")
    bridge.process_plan(filename)
else:
    print(f"File {filename} not found!")
