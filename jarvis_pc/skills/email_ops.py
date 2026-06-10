import os.path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        return None

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def read_latest_emails(count=3) -> str:
    service = get_gmail_service()
    if not service:
        return "I cannot access your emails, sir. Please place your credentials.json file in the root folder."
    
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=count).execute()
        messages = results.get('messages', [])

        if not messages:
            return "You have no unread emails, sir."
            
        email_summary = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
            email_summary.append(f"From {sender}: {subject}")
            
        return "Here are your latest unread emails: " + ". ".join(email_summary)
    except Exception as e:
        return f"An error occurred while fetching emails: {str(e)}"
