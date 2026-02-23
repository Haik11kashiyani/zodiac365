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

def generate_daily(today, active_signs=None):
    if active_signs is None:
        active_signs = SIGNS
    print(f"--- 🌞 GENERATING DAILY VIDEOS ({len(active_signs)} signs) ---")
    for sign in active_signs:
        if not generator_zodiac.generate_zodiac_video('daily', sign, today.strftime("%B %d, %Y")):
            print(f"❌ Failed to generate daily video for {sign}")
    
    # Wildcard Special (Daily Only) - only run if last batch of signs
    if active_signs[-1] == SIGNS[-1]:
        print("--- 🃏 GENERATING WILDCARD VIDEO ---")
        if random.choice([True, False]):
            s1, s2 = random.sample(SIGNS, 2)
            generator_zodiac.generate_zodiac_video('compatibility', f"{s1} vs {s2}", str(today))
        else:
            topics = ["Mercury Retrograde", "Full Moon Ritual", "Lucky Numbers", "Spirit Animals"]
            generator_zodiac.generate_zodiac_video('special', random.choice(topics), str(today))

def generate_weekly(today, active_signs=None):
    if active_signs is None:
        active_signs = SIGNS
    print(f"--- 📅 GENERATING WEEKLY FORECASTS ({len(active_signs)} signs) ---")
    # Calculate next week range (starting tomorrow if run today, or just "This Week")
    # Assuming "Weekly" means the upcoming week.
    start_of_week = today
    end_of_week = today + datetime.timedelta(days=6)
    date_range = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
    
    for sign in active_signs:
        if generator_zodiac.generate_zodiac_video('weekly', sign, date_range):
            print(f"  ✅ {sign} weekly plan created.")
        else:
            print(f"  ❌ Failed to generate weekly for {sign}")
    print(f"📊 Weekly generation complete for {len(active_signs)} signs.")

def run_empire():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=['daily', 'weekly', 'all'], default='all', help="Generation mode")
    parser.add_argument("--signs", type=str, default=None, help="Comma-separated list of zodiac signs to generate (e.g. 'Aries,Taurus,Gemini,Cancer'). If omitted, all 12 signs are generated.")
    args = parser.parse_args()

    today = datetime.date.today()

    # Determine which signs to generate
    if args.signs:
        active_signs = [s.strip() for s in args.signs.split(',') if s.strip() in SIGNS]
        if not active_signs:
            print(f"❌ FATAL: No valid signs in --signs '{args.signs}'. Valid: {', '.join(SIGNS)}")
            sys.exit(1)
    else:
        active_signs = list(SIGNS)

    print(f"🚀 GENERATING EMPIRE CONTENT FOR {today} (Mode: {args.mode.upper()}, Signs: {', '.join(active_signs)})...")

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
            generate_daily(today, active_signs)
            
            # Monthly/Yearly Logic (Staggered Daily)
            day_of_month = today.day
            if 1 <= day_of_month <= 12:
                target_sign = SIGNS[day_of_month - 1]
                if target_sign in active_signs:
                    print(f"--- 📅 GENERATING MONTHLY CONTENT FOR {target_sign.upper()} ---")
                    generator_zodiac.generate_zodiac_video('monthly', target_sign, today.strftime("%B %Y"))
                    
                    if today.month == 1:
                        print(f"--- 🎆 GENERATING YEARLY CONTENT FOR {target_sign.upper()} ---")
                        generator_zodiac.generate_zodiac_video('yearly', target_sign, "2026")

    if args.mode in ['weekly', 'all']:
        generate_weekly(today, active_signs)

    # Verify plans were created
    import glob
    created_plans = glob.glob("plan_*.json")
    print(f"📋 Total plan files ready for processing: {len(created_plans)}")
    if len(created_plans) == 0:
        print("❌ FATAL: No plan files created! Aborting.")
        sys.exit(1)

if __name__ == "__main__": run_empire()
