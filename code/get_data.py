import os
import csv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define Gmail API scope (Read-Only)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get project root directory
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")
INPUT_DIR = os.path.join(BASE_DIR, "input")

CLIENT_SECRET_FILE = os.path.join(SECRETS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SECRETS_DIR, "token.json")
OUTPUT_CSV = os.path.join(INPUT_DIR, "emails.csv")

def get_gmail_service():
    """Authenticate and return the Gmail API service."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_emails(service, label_ids, email_type, max_results=1000):
    """
    Fetch emails from Gmail based on the given label (inbox or sent).
    
    Parameters:
        service: Authenticated Gmail API service
        label_ids: Label for filtering emails (e.g., "INBOX" or "SENT")
        email_type: "Received" or "Sent"
        max_results: Maximum emails to fetch

    Returns:
        List of dictionaries containing email data.
    """
    results = service.users().messages().list(userId="me", labelIds=label_ids, maxResults=max_results).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()

        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        recipient = next((h["value"] for h in headers if h["name"] == "To"), "Unknown Recipient")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
        snippet = msg_data.get("snippet", "No snippet available")

        emails.append({
            "id": msg["id"],
            "type": email_type,  # "Received" or "Sent"
            "subject": subject,
            "sender": sender if email_type == "Received" else recipient,  # Normalize sender/recipient
            "snippet": snippet,
            "date": date
        })

    return emails

def save_to_csv(emails):
    """Save email data to a CSV file."""
    os.makedirs(INPUT_DIR, exist_ok=True)  # Ensure input folder exists

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "type", "subject", "sender", "snippet", "date"])
        writer.writeheader()
        writer.writerows(emails)

if __name__ == "__main__":
    service = get_gmail_service()

    # Fetch received emails (INBOX) and sent emails (SENT)
    received_emails = get_emails(service, label_ids=["INBOX"], email_type="Received", max_results=1000)
    sent_emails = get_emails(service, label_ids=["SENT"], email_type="Sent", max_results=1000)

    # Combine both into one list
    all_emails = received_emails + sent_emails

    # Save to CSV
    save_to_csv(all_emails)

    print(f"✅ Successfully saved {len(all_emails)} emails (Received + Sent) to '{OUTPUT_CSV}'!")

    # Close the service
    service.close()