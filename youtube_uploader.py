import os
import json
import datetime
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """
    Authenticate with YouTube API using token.json or environment variables.
    Supports automatic token refresh using CLIENT_ID and CLIENT_SECRET.
    """
    token_file = os.path.join(os.path.dirname(__file__), 'token.json')
    print(f"🔍 Looking for token at: {token_file}")
    
    # Get client credentials from environment (for token refresh)
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    
    if not os.path.exists(token_file):
        print("⚠️ No token.json found. Cannot upload to YouTube.")
        return None

    try:
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            print(f"✅ Token loaded. Keys present: {list(token_data.keys())}")
        
        # Add client_id and client_secret if not in token (needed for refresh)
        if client_id and 'client_id' not in token_data:
            token_data['client_id'] = client_id
        if client_secret and 'client_secret' not in token_data:
            token_data['client_secret'] = client_secret
            
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        
        # Check if token is expired and refresh if possible
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expired, attempting refresh...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
                
                # Save refreshed token back to file
                with open(token_file, 'w') as f:
                    json.dump({
                        'token': creds.token,
                        'refresh_token': creds.refresh_token,
                        'token_uri': creds.token_uri,
                        'client_id': creds.client_id,
                        'client_secret': creds.client_secret,
                        'scopes': list(creds.scopes)
                    }, f)
            except Exception as refresh_error:
                print(f"⚠️ Token refresh failed: {refresh_error}")
        
        return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Error loading YouTube token: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_metadata(data):
    """Generate Viral Title, Description, Tags using AI data or Dynamic Templates."""
    
    # 1. Prefer AI-Generated Metadata if available
    ai_title = data.get('youtube_title')
    ai_desc = data.get('youtube_description')
    ai_tags = data.get('youtube_tags')
    
    target = data.get('target', 'Zodiac')
    mode = data.get('type', 'daily')
    date_str = data.get('date', 'Today')
    emoji = get_emoji(target)
    current_year = datetime.datetime.now().year
    
    # --- TITLE STRATEGY ---
    if ai_title:
        # trust the AI but ensure hashtags
        final_title = f"{emoji} {ai_title} #shorts #viral"
    else:
        # Fallback Dynamic Templates
        if mode == 'daily':
            final_title = f"{emoji} {target}: {date_str} Prediction 🔮 #shorts #viral"
        elif mode == 'monthly':
            final_title = f"{emoji} {target}: {date_str} Forecast! ⚠️ #shorts"
        elif mode == 'yearly':
            final_title = f"{emoji} {target} {current_year}: Full Prediction 🔮 #shorts"
        elif mode == 'compatibility':
            final_title = f"{target}: Only One Winner? 💔❤️ #shorts #viral"
        else:
            final_title = f"{data.get('title', 'Horoscope')} #shorts #viral"

    # --- DESCRIPTION STRATEGY ---
    if ai_desc:
        description_body = ai_desc
    else:
        description_body = f"✨ Your {mode} prediction for {target} ({date_str}). Discover your destiny!"

    description = f"""{final_title}

{description_body}

📅 Date: {date_str}
🔥 Sign: {target}

👇 **Subscribe for Daily Horoscopes!**
https://www.youtube.com/@Zodiac365?sub_confirmation=1

#astrology #zodiac #{target.lower().replace(' ', '')} #horoscope #dailyhoroscope #{mode} #shorts #viral #astrologyreadings #zodiacsigns #tarot #manifestation #spirituality
"""

    # --- TAGS STRATEGY ---
    if ai_tags and isinstance(ai_tags, list):
        tags = ai_tags
        # Ensure compulsory tags exist
        for t in ["shorts", "viral", "astrology", target.lower()]:
            if t not in tags: tags.append(t)
    else:
        tags = [
            "astrology", "zodiac", "horoscope", "shorts", "viral", "fyp", 
            "daily horoscope", "astrology today", "zodiac signs", 
            target.lower(), f"{target.lower()} horoscope", f"{target.lower()} {current_year}"
        ]
    
    # YouTube Title Limit Check (100 chars)
    if len(final_title) > 100:
        # Keep hashtags, truncate middle if needed, or just hard chop
        # Logic: title... #shorts #viral
        suffix = " #shorts #viral"
        limit = 100 - len(suffix)
        clean_title = final_title.replace(suffix, "")
        final_title = clean_title[:limit-1] + "…" + suffix

    return final_title, description, tags

def get_emoji(sign):
    emojis = {
        "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍",
        "Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"
    }
    # Simple check if sign name is in target string
    for k,v in emojis.items():
        if k in sign: return v
    return "🔮"

def upload_video(file_path, data):
    youtube = get_authenticated_service()
    if not youtube: return False

    title, description, tags = generate_metadata(data)
    
    print(f"📺 Uploading to YouTube: {title}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22' # People & Blogs
        },
        'status': {
            'privacyStatus': 'public', # CHANGE TO 'private' FOR TESTING IF NEEDED
            'selfDeclaredMadeForKids': False
        }
    }

    try:
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   Uploaded {int(status.progress() * 100)}%")
        
        print(f"✅ Upload Complete! Video ID: {response.get('id')}")
        return True
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        return False
