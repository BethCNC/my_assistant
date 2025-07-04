import os
import base64
import re
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to your credentials.json file
CREDENTIALS_FILE = 'client_secret_510608642536-rn43nlpin83e7vtksm05ci7u7qkcp7nf.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'

# Search queries
APPT_QUERY = 'subject:(appointment OR confirmed OR schedule) after:2024/03/01'
PREP_QUERY = 'from:"Rachel Lee Patient Advocacy" prep'


def authenticate_gmail():
    """Authenticate and return Gmail API service."""
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
    """Search for messages matching the query."""
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = response.get('messages', [])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []


def get_message_details(service, user_id: str, msg_id: str) -> Dict:
    """Get the details of a message by ID."""
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        snippet = message.get('snippet', '')
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
        else:
            body = base64.urlsafe_b64decode(message['payload']['body'].get('data', '')).decode('utf-8', errors='ignore')
        return {
            'id': msg_id,
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'date': headers.get('Date', ''),
            'snippet': snippet,
            'body': body,
        }
    except HttpError as error:
        print(f'An error occurred: {error}')
        return {}


def extract_appointment_info(email: Dict) -> Dict:
    """Extract appointment details from email content."""
    # Simple regex-based extraction (customize as needed)
    date_match = re.search(r'(\b\d{1,2}/\d{1,2}/\d{2,4}\b)', email['body'])
    time_match = re.search(r'(\b\d{1,2}:\d{2}\s?(AM|PM|am|pm)\b)', email['body'])
    location_match = re.search(r'(Location:.*)', email['body'])
    return {
        'subject': email['subject'],
        'from': email['from'],
        'date': date_match.group(1) if date_match else email['date'],
        'time': time_match.group(1) if time_match else '',
        'location': location_match.group(1) if location_match else '',
        'snippet': email['snippet'],
    }


def extract_prep_info(email: Dict) -> Dict:
    """Extract prep instructions from Rachel Lee Patient Advocacy emails."""
    # Look for lines with 'prep' in them
    prep_lines = [line for line in email['body'].split('\n') if 'prep' in line.lower()]
    return {
        'subject': email['subject'],
        'from': email['from'],
        'date': email['date'],
        'prep_instructions': prep_lines,
        'snippet': email['snippet'],
    }


def main():
    service = authenticate_gmail()
    user_id = 'me'

    print('Searching for appointment confirmation emails...')
    appt_msgs = search_messages(service, user_id, APPT_QUERY)
    appt_details = []
    for msg in appt_msgs:
        details = get_message_details(service, user_id, msg['id'])
        if details:
            appt_details.append(extract_appointment_info(details))

    print('Searching for Rachel Lee Patient Advocacy prep emails...')
    prep_msgs = search_messages(service, user_id, PREP_QUERY)
    prep_details = []
    for msg in prep_msgs:
        details = get_message_details(service, user_id, msg['id'])
        if details:
            prep_details.append(extract_prep_info(details))

    # Output results
    print('\n--- Appointment Confirmations ---')
    for appt in appt_details:
        print(appt)

    print('\n--- Prep Instructions ---')
    for prep in prep_details:
        print(prep)

    # Optionally, save to CSV/JSON for Google Doc import
    # (Add code here if needed)

if __name__ == '__main__':
    main() 