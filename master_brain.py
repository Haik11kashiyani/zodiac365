import datetime, generator_zodiac, generator_tarot

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def run_empire():
    today = datetime.date.today()
    day, month = today.day, today.month
    
    # 1. Daily Tarot
    generator_tarot.generate_reading(str(today))

    # 2. Strategic Zodiac Loop
    if month == 1 and day <= 12: # Jan Grand Opening
        target = SIGNS[day-1]
        generator_zodiac.generate_zodiac_video('monthly', target, "Jan 2026")
        generator_zodiac.generate_zodiac_video('yearly', target, "2026")
    elif day <= 12: # Monthly Pulse
        generator_zodiac.generate_zodiac_video('monthly', SIGNS[day-1], today.strftime("%B %Y"))
    else: # Library Build
        mode = 'birthday' if day % 2 == 0 else 'compatibility'
        target = today.strftime("%B %d") if mode == 'birthday' else "Scorpio vs Leo"
        generator_zodiac.generate_zodiac_video(mode, target, str(today))

if __name__ == "__main__": run_empire()
