import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

CREDENTIALS_FILE = 'client_secret_510608642536-rn43nlpin83e7vtksm05ci7u7qkcp7nf.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'
MARKDOWN_FILE = 'medical_appointments_prep_doc.md'


def authenticate_google():
    """Authenticate and return Google Docs and Drive service objects."""
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
    
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    return docs_service, drive_service


def create_google_doc(docs_service, drive_service):
    """Create a new Google Doc and return its ID."""
    doc = {
        'title': 'Medical Appointments & Prep'
    }
    
    result = docs_service.documents().create(body=doc).execute()
    doc_id = result.get('documentId')
    
    print(f"Created Google Doc: https://docs.google.com/document/d/{doc_id}")
    return doc_id


def read_markdown_file():
    """Read and parse the markdown file content."""
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def format_document_content(docs_service, doc_id, markdown_content):
    """Add formatted content to the Google Doc."""
    
    # Parse markdown and convert to Google Docs format
    requests = []
    
    # Add title
    requests.append({
        'insertText': {
            'location': {'index': 1},
            'text': 'Medical Appointments & Prep\n\n'
        }
    })
    
    # Add overview section header
    requests.append({
        'insertText': {
            'location': {'index': 1},
            'text': 'Overview\n\n'
        }
    })
    
    # Create table for diagnoses and symptoms
    requests.append({
        'insertTable': {
            'location': {'index': 1},
            'rows': 2,
            'columns': 2
        }
    })
    
    # Add main content sections
    main_content = """
Main Content

Medical To-Do & Prep Checklist:
□ Rheumatology Prep - Review attached documents
□ GI Prep - Follow attached instructions  
□ Cardiology Prep - Complete pre-appointment requirements
□ Allergy Prep - Prepare for allergy testing
□ Bring current medication list to all appointments
□ Fast as required for specific tests
□ Complete any required lab work
□ Bring insurance cards and ID
□ Prepare questions for each specialist

Upcoming Medical Appointments:
• [Date] - [Doctor/Specialist] - [Location] - [Time]
• [Date] - [Doctor/Specialist] - [Location] - [Time]
• [Date] - [Doctor/Specialist] - [Location] - [Time]

Reference - Prep Instructions:
(Collapsible section with full prep email details)
"""
    
    requests.append({
        'insertText': {
            'location': {'index': 1},
            'text': main_content
        }
    })
    
    # Apply formatting
    requests.extend([
        # Format title
        {
            'updateTextStyle': {
                'range': {'startIndex': 1, 'endIndex': 29},
                'textStyle': {
                    'fontSize': {'magnitude': 18, 'unit': 'PT'},
                    'bold': True
                },
                'fields': 'fontSize,bold'
            }
        },
        # Format section headers
        {
            'updateTextStyle': {
                'range': {'startIndex': 31, 'endIndex': 40},
                'textStyle': {
                    'fontSize': {'magnitude': 14, 'unit': 'PT'},
                    'bold': True
                },
                'fields': 'fontSize,bold'
            }
        }
    ])
    
    # Execute all requests
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()


def main():
    """Main function to create and populate the Google Doc."""
    try:
        # Authenticate
        docs_service, drive_service = authenticate_google()
        
        # Create new document
        doc_id = create_google_doc(docs_service, drive_service)
        
        # Read markdown content
        markdown_content = read_markdown_file()
        
        # Format and populate document
        format_document_content(docs_service, doc_id, markdown_content)
        
        print(f"\n✅ Google Doc created successfully!")
        print(f"📄 Document URL: https://docs.google.com/document/d/{doc_id}")
        print(f"📝 You can now edit and share this document as needed.")
        
    except FileNotFoundError:
        print(f"❌ Error: {MARKDOWN_FILE} not found. Please ensure the file exists.")
    except HttpError as error:
        print(f"❌ Google API Error: {error}")
    except Exception as error:
        print(f"❌ Unexpected error: {error}")


if __name__ == '__main__':
    main() 