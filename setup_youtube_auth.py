import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle/token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def setup_auth(client_secret_file='client_secret.json'):
    creds = None
    token_file = 'token.json'
    
    if os.path.exists(token_file):
        print("✅ Found existing token.json")
        try:
            with open(token_file, 'r') as token:
                from google.oauth2.credentials import Credentials
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
        except Exception as e:
            print(f"⚠️ Error loading token: {e}")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_file):
                print(f"❌ Error: {client_secret_file} not found! Please place your client secret json here.")
                print("   (Download it from Google Cloud Console > APIs & Services > Credentials)")
                return

            print("🚀 Launching browser for login...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        print("💾 Saving token.json...")
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
    print("✨ Authentication Setup Complete! token.json is ready.")

if __name__ == '__main__':
    # You can pass the path to your downloaded client secret json
    # Look for files like 'client_secret_....apps.googleusercontent.com.json'
    secret_files = [f for f in os.listdir('.') if f.startswith('client_secret') and f.endswith('.json')]
    if secret_files:
        setup_auth(secret_files[0])
    else:
        setup_auth() # Will look for 'client_secret.json'
