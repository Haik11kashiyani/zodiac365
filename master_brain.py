import datetime, json, os, random
import generator_zodiac, generator_tarot, choreographer

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def run_empire():
    today = datetime.date.today()
    day, month = today.day, today.month
    
    # 1. ALWAYS Daily Tarot
    generator_tarot.generate_reading(str(today))

    # 2. STRATEGY Logic
    if month == 1 and day <= 12: # Jan Grand Opening
        target = SIGNS[day-1]
        generator_zodiac.generate_zodiac_video('monthly', target, "January 2026")
        generator_zodiac.generate_zodiac_video('yearly', target, "2026")
    elif day <= 12: # Monthly Pulse
        generator_zodiac.generate_zodiac_video('monthly', SIGNS[day-1], today.strftime("%B %Y"))
    elif day == 13: # NEW: The Wildcard Day
        # The system thinks of something new every month on the 13th
        topics = ["Mercury Retrograde", "Full Moon Ritual", "Black Moon Lilith", "Numerology 8", "Evil Eye Protection"]
        generator_zodiac.generate_zodiac_video('special', random.choice(topics), str(today))
    else: # Library Build
        mode = 'birthday' if day % 2 == 0 else 'compatibility'
        target = today.strftime("%B %d") if mode == 'birthday' else f"{random.choice(SIGNS)} vs {random.choice(SIGNS)}"
        generator_zodiac.generate_zodiac_video(mode, target, str(today))

if __name__ == "__main__":
    run_empire()
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]:
        choreographer.polish(f)
