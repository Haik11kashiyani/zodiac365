import datetime
import generator_tarot
import generator_zodiac

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def run_empire():
    today = datetime.date.today()
    day = today.day
    month = today.month
    
    print(f"👑 EMPIRE BRAIN: Processing {today}...")

    # 1. ALWAYS Run Daily Tarot
    generator_tarot.generate_reading(str(today))

    # 2. STRATEGY LOGIC
    if month == 1 and day <= 12:
        # --- THE GRAND OPENING (Jan 1-12) ---
        # Video 2: Monthly Forecast (For the Sign corresponding to the Day)
        # Video 3: Yearly Forecast (For the Sign corresponding to the Day)
        # Day 1 = Aries, Day 2 = Taurus...
        sign_idx = day - 1
        target_sign = SIGNS[sign_idx]
        
        generator_zodiac.generate_zodiac_video('monthly', target_sign, "January 2026")
        generator_zodiac.generate_zodiac_video('yearly', target_sign, "2026")

    elif day <= 12:
        # --- THE MONTHLY PULSE (Feb-Dec, Days 1-12) ---
        # Video 2: Monthly Forecast for current month
        sign_idx = day - 1
        target_sign = SIGNS[sign_idx]
        month_name = today.strftime("%B")
        generator_zodiac.generate_zodiac_video('monthly', target_sign, f"{month_name} 2026")

    else:
        # --- THE LIBRARY BUILD (Days 13+) ---
        # Video 2: Birthday Secret OR Compatibility
        # Alternate days: Even = Birthday, Odd = Compatibility
        if day % 2 == 0:
            # Birthday Video
            birthday_str = today.strftime("%B %d")
            generator_zodiac.generate_zodiac_video('birthday', birthday_str, str(today))
        else:
            # Compatibility Video (Random Pair)
            import random
            s1 = random.choice(SIGNS)
            s2 = random.choice(SIGNS)
            generator_zodiac.generate_zodiac_video('compatibility', f"{s1} vs {s2}", str(today))

if __name__ == "__main__":
    run_empire()
