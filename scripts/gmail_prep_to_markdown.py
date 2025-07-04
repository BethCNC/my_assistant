import os
import base64
import re
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'client_secret_510608642536-rn43nlpin83e7vtksm05ci7u7qkcp7nf.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'
MARKDOWN_FILE = 'medical_prep_emails.md'

# Broader search: from Rachel, with prep or preparation in subject/body
PREP_QUERY = 'from:(rachel) (prep OR preparation)'


def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service


def search_messages(service, user_id: str, query: str) -> List[Dict]:
    try:
        response = service.users().messages().list(userId=user_id, q=query, maxResults=30).execute()
        messages = response.get('messages', [])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []


def get_message_details(service, user_id: str, msg_id: str) -> Dict:
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        snippet = message.get('snippet', '')
        body = ''
        # Try to get the plain text part
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
                elif part['mimeType'] == 'text/html':
                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    # Strip HTML tags for markdown
                    body = re.sub('<[^<]+?>', '', html)
        else:
            data = message['payload']['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        return {
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'date': headers.get('Date', ''),
            'body': body if body else snippet,
        }
    except HttpError as error:
        print(f'An error occurred: {error}')
        return {}


def write_markdown(emails: List[Dict], filename: str):
    with open(filename, 'w') as f:
        f.write('# Medical Prep Emails\n\n')
        for i, email in enumerate(emails, 1):
            f.write(f'## {i}. {email["subject"]}\n')
            f.write(f'- **From:** {email["from"]}\n')
            f.write(f'- **Date:** {email["date"]}\n\n')
            f.write('---\n')
            f.write(f'{email["body"]}\n')
            f.write('\n---\n\n')
    print(f'Wrote {len(emails)} emails to {filename}')


def main():
    service = authenticate_gmail()
    user_id = 'me'
    print('Searching for Rachel Lee prep/preparation emails...')
    prep_msgs = search_messages(service, user_id, PREP_QUERY)
    emails = []
    for msg in prep_msgs:
        details = get_message_details(service, user_id, msg['id'])
        if details:
            emails.append(details)
    write_markdown(emails, MARKDOWN_FILE)

if __name__ == '__main__':
    main() 