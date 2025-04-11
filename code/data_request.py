import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define Gmail API scope (Read-Only)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    """Authenticate and return the Gmail API service."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=8080)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def check_email_availability(service):
    """Check if emails are available."""
    try:
        results = service.users().messages().list(userId="me", maxResults=1).execute()
        messages = results.get("messages", [])
        if messages:
            print("✅ Connection successful! Emails are available.")
        else:
            print("⚠️ Connection successful, but no emails found.")
    except Exception as e:
        print(f"❌ Error checking emails: {e}")

if __name__ == "__main__":
    print("🔄 Checking Gmail connection...")
    service = get_gmail_service()
    check_email_availability(service)

    print("✅ Connection successful! Emails are available.")