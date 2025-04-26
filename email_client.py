# email_client.py

import os.path
import base64
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import re
import google.auth

# If modifying SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    def __init__(self, credentials_file='credentials.json'):
        self.creds = None
        self.service = None
        self.credentials_file = credentials_file
        self.authenticate()

    def authenticate(self):
        """Handles OAuth2 login and token refresh."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_latest_emails(self, max_results=5):
        """Fetches the latest emails."""
        results = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_data['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
            sender = next((header['value'] for header in headers if header['name'] == 'From'), "Unknown Sender")
            snippet = msg_data.get('snippet', '')
            
            # Try to decode full message body if possible
            parts = msg_data['payload'].get('parts', [])
            body = ''
            if parts:
                body = base64.urlsafe_b64decode(parts[0]['body']['data']).decode('utf-8', errors='ignore')
            else:
                body = snippet

            emails.append({
                'subject': subject,
                'sender': sender,
                'body': body
            })

        return emails
    
    def create_draft(self, to, subject, message_text):

        message = MIMEText(message_text)
        
        # Make sure 'to' is properly formatted
        # If it's not already a valid email format, try to clean it
        if not re.match(r"[^@]+@[^@]+\.[^@]+", to) and not re.match(r".*<[^@]+@[^@]+\.[^@]+>", to):
            print(f"Warning: Potentially invalid email address format: {to}")
            # Try to extract an email if possible or use a fallback
        
        message['to'] = to
        message['from'] = self.user_email  # Add sender email
        message['subject'] = subject
        
        # Encode the message properly
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {'message': {'raw': raw_message}}

        try:
            draft = self.service.users().drafts().create(userId='me', body=create_message).execute()
            print(f"✉️ Draft created: {draft['id']}")
            return draft
        except Exception as e:
            print(f"Error creating draft: {str(e)}")
            print(f"To address was: '{to}'")
            raise

