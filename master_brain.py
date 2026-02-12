import datetime, random, generator_zodiac, generator_tarot, json, os, sys, glob

# Force UTF-8 for Windows Consoles
sys.stdout.reconfigure(encoding='utf-8')

with open("config.json", "r") as f:
    CONFIG = json.load(f)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def clean_workspace():
    """Removes old plan plans to prevent duplicate video generation."""
    files = glob.glob("plan_*.json")
    for f in files:
        try: os.remove(f)
        except: pass
    print(f"🧹 Cleaned {len(files)} old plans.")

import argparse

def generate_daily(today):
    print("--- 🌞 GENERATING DAILY VIDEOS ---")
    for sign in SIGNS:
        if not generator_zodiac.generate_zodiac_video('daily', sign, today.strftime("%B %d, %Y")):
            print(f"❌ Failed to generate daily video for {sign}")
    
    # Wildcard Special (Daily Only)
    print("--- 🃏 GENERATING WILDCARD VIDEO ---")
    if random.choice([True, False]):
        s1, s2 = random.sample(SIGNS, 2)
        generator_zodiac.generate_zodiac_video('compatibility', f"{s1} vs {s2}", str(today))
    else:
        topics = ["Mercury Retrograde", "Full Moon Ritual", "Lucky Numbers", "Spirit Animals"]
        generator_zodiac.generate_zodiac_video('special', random.choice(topics), str(today))

def generate_weekly(today):
    print("--- 📅 GENERATING WEEKLY FORECASTS ---")
    # Calculate next week range (starting tomorrow if run today, or just "This Week")
    # Assuming "Weekly" means the upcoming week.
    start_of_week = today
    end_of_week = today + datetime.timedelta(days=6)
    date_range = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
    
    for sign in SIGNS:
        if generator_zodiac.generate_zodiac_video('weekly', sign, date_range):
            print(f"  ✅ {sign} weekly plan created.")
        else:
            print(f"  ❌ Failed to generate weekly for {sign}")
    print(f"📊 Weekly generation complete for {len(SIGNS)} signs.")

def run_empire():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=['daily', 'weekly', 'all'], default='all', help="Generation mode")
    args = parser.parse_args()

    today = datetime.date.today()
    print(f"🚀 GENERATING EMPIRE CONTENT FOR {today} (Mode: {args.mode.upper()})...")

    # CRITICAL: Clean old plans so fresh content is generated every run.
    # Without this, stale "pending" plan files from Git checkout trigger
    # the MANUAL OVERRIDE check and skip all AI generation.
    clean_workspace()

    if args.mode in ['daily', 'all']:
        # Delayed Start Check: Jan 9, 2026 (Friday)
        start_date = datetime.date(2026, 1, 9)
        if today < start_date:
            print(f"⏳ Automation Standby: Daily content is scheduled to start on {start_date}. Today is {today}. Skipping.")
        else:
            generate_daily(today)
            
            # Monthly/Yearly Logic (Staggered Daily)
            day_of_month = today.day
            if 1 <= day_of_month <= 12:
                target_sign = SIGNS[day_of_month - 1] 
                print(f"--- 📅 GENERATING MONTHLY CONTENT FOR {target_sign.upper()} ---")
                generator_zodiac.generate_zodiac_video('monthly', target_sign, today.strftime("%B %Y"))
                
                if today.month == 1:
                    print(f"--- 🎆 GENERATING YEARLY CONTENT FOR {target_sign.upper()} ---")
                    generator_zodiac.generate_zodiac_video('yearly', target_sign, "2026")

    if args.mode in ['weekly', 'all']:
        generate_weekly(today)

if __name__ == "__main__": run_empire()
