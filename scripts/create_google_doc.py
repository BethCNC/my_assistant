#!/usr/bin/env python3
"""
Script to create a Google Doc from the medical appointments markdown file.
"""

import os
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]
# NOTE: If you change the scopes above, delete token.json and re-authenticate.

CREDENTIALS_FILE = 'client_secret_510608642536-rn43nlpin83e7vtksm05ci7u7qkcp7nf.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'
MARKDOWN_FILE = 'medical_appointments_prep_doc.md'
DOCUMENT_ID = '1YVs-cNUoYHxUyipVsXIQGiK9_2emeIQgljDBtjEFcYM'


def authenticate_google():
    """Authenticate and return Google Docs service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def parse_markdown_content():
    """Parse the markdown file and extract content."""
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract sections
    sections = {}
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[2:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def create_google_doc(service, title="Medical Appointments & Prep"):
    """Create a new Google Doc with the medical content."""
    try:
        # Create a new document
        doc = service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')
        print(f'Created document with ID: {doc_id}')
        
        # Parse markdown content
        sections = parse_markdown_content()
        
        # Prepare requests for batch update
        requests = []
        
        # Add title
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f"{title}\n\n"
            }
        })
        
        # Add content sections
        current_index = len(title) + 3
        
        # Add overview section with table-like structure
        overview_text = """CURRENT DIAGNOSES & SYMPTOMS
        
Diagnoses:
• Hashimoto's Thyroiditis
• Fibromyalgia  
• ADHD
• Anxiety Disorder
• Chronic Fatigue Syndrome
• POTS (Postural Orthostatic Tachycardia Syndrome)
• Small Fiber Neuropathy
• Gastroparesis
• MCAS (Mast Cell Activation Syndrome)
• Hypothyroidism
• Chronic Pain
• Sleep Disorders

Current Symptoms:
• Chronic fatigue and exhaustion
• Joint pain and stiffness
• Brain fog and concentration issues
• Heart palpitations
• Digestive issues and nausea
• Temperature regulation problems
• Sleep disturbances
• Muscle weakness
• Headaches
• Dizziness
• Skin sensitivity
• Memory issues

"""
        
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': overview_text
            }
        })
        current_index += len(overview_text)
        
        # Add main content sections
        main_content = """
MEDICAL TO-DO & PREP CHECKLIST

Pre-Appointment Prep:
☐ Fast for 12 hours before blood work
☐ Bring current medication list
☐ Bring recent lab results
☐ Stop certain medications 48hrs before (check with doctor)
☐ Prepare symptom diary for past 2 weeks
☐ Write down questions to ask doctor
☐ Bring insurance cards and ID
☐ Arrive 15 minutes early

Rheumatology Prep:
☐ Complete joint pain assessment form
☐ Bring list of current supplements
☐ Document morning stiffness duration
☐ Note any new joint symptoms

GI Prep:
☐ Complete dietary diary for 1 week
☐ List all digestive symptoms
☐ Note trigger foods
☐ Bring previous GI test results

Cardiology Prep:
☐ Record heart rate and blood pressure daily
☐ Note palpitation episodes with triggers
☐ Bring EKG results from primary care
☐ List all cardiac symptoms

Allergy Prep:
☐ Stop antihistamines 5 days before testing
☐ Avoid alcohol 24 hours before
☐ Wear comfortable, loose-fitting clothes
☐ Bring list of suspected allergens

General Health Tasks:
☐ Schedule annual mammogram
☐ Update emergency contact information
☐ Review and update medication list
☐ Get flu shot (if not done)
☐ Schedule dental cleaning
☐ Order prescription refills
☐ Update health insurance information

UPCOMING MEDICAL APPOINTMENTS

January 2025:
• Jan 15, 2025 - Rheumatology Follow-up
• Jan 22, 2025 - Cardiology Consultation
• Jan 29, 2025 - GI Specialist

February 2025:
• Feb 5, 2025 - Allergy Testing
• Feb 12, 2025 - Endocrinology
• Feb 19, 2025 - Neurology Consultation

March 2025:
• Mar 5, 2025 - Primary Care Check-up
• Mar 12, 2025 - Mental Health Follow-up

Pending Scheduling:
• Dermatology (waiting for referral)
• Orthopedics (pending insurance approval)
• Sleep Study (scheduling in progress)

"""
        
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': main_content
            }
        })
        current_index += len(main_content)
        
        # Add footer
        footer_text = f"\nLast updated: {datetime.now().strftime('%B %d, %Y')}\n"
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': footer_text
            }
        })
        
        # Execute batch update
        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print(f'Successfully created Google Doc: {title}')
        print(f'Document URL: https://docs.google.com/document/d/{doc_id}/edit')
        
        return doc_id
        
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def insert_diagnoses_and_symptoms(service, document_id):
    DIAGNOSES = [
        "Hashimoto's Thyroiditis",
        "Fibromyalgia",
        "ADHD",
        "Anxiety Disorder",
        "Chronic Fatigue Syndrome",
        "POTS (Postural Orthostatic Tachycardia Syndrome)",
        "Small Fiber Neuropathy",
        "Gastroparesis",
        "MCAS (Mast Cell Activation Syndrome)",
        "Hypothyroidism",
        "Chronic Pain",
        "Sleep Disorders"
    ]
    SYMPTOMS = [
        "Chronic fatigue and exhaustion",
        "Joint pain and stiffness",
        "Brain fog and concentration issues",
        "Heart palpitations",
        "Digestive issues",
        "Temperature regulation problems",
        "Sleep disturbances",
        "Muscle weakness",
        "Dizziness or lightheadedness",
        "Allergic reactions (rashes, hives, swelling)",
        "Headaches",
        "Anxiety or mood swings"
    ]

    # Get the document content
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    # Find the indices for Diagnosis and Symptoms
    diagnosis_idx = None
    symptoms_idx = None
    for i, el in enumerate(content):
        if 'paragraph' in el:
            elements = el['paragraph'].get('elements', [])
            for e in elements:
                text = e.get('textRun', {}).get('content', '').strip().lower()
                if text == 'diagnosis':
                    diagnosis_idx = el['startIndex']
                if text == 'symptoms':
                    symptoms_idx = el['startIndex']

    requests = []
    if diagnosis_idx:
        requests.append({
            'insertText': {
                'location': {'index': diagnosis_idx + 1},
                'text': '\n' + '\n'.join(f'• {d}' for d in DIAGNOSES) + '\n'
            }
        })
    if symptoms_idx:
        requests.append({
            'insertText': {
                'location': {'index': symptoms_idx + 1},
                'text': '\n' + '\n'.join(f'• {s}' for s in SYMPTOMS) + '\n'
            }
        })
    if requests:
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        print('✅ Diagnoses and symptoms inserted.')
    else:
        print('❌ Could not find Diagnosis or Symptoms headings in the document.')


def find_first_normal_paragraph_index(doc):
    for element in doc["body"]["content"]:
        if "paragraph" in element:
            style = element["paragraph"].get("paragraphStyle", {})
            if style.get("namedStyleType") == "NORMAL_TEXT":
                return element["endIndex"]
    return 1


def find_last_normal_paragraph_index(doc):
    last_index = 1
    for element in doc["body"]["content"]:
        if "paragraph" in element:
            style = element["paragraph"].get("paragraphStyle", {})
            if style.get("namedStyleType") == "NORMAL_TEXT":
                last_index = element["endIndex"]
    return last_index


def find_second_to_last_normal_paragraph_index(doc):
    indices = []
    for element in doc["body"]["content"]:
        if "paragraph" in element:
            style = element["paragraph"].get("paragraphStyle", {})
            if style.get("namedStyleType") == "NORMAL_TEXT":
                indices.append(element["endIndex"])
    if len(indices) >= 2:
        return indices[-2]
    elif indices:
        return indices[0]
    return 1


def insert_diagnosis_table(service, document_id):
    diagnoses = [
        ("Diagnosis", "Original Diagnosis Date"),
        ("Hashimoto's Thyroiditis", "2017-04-15"),
        ("Fibromyalgia", "2018-09-10"),
        ("ADHD", "2020-06-01"),
        ("Anxiety Disorder", "2015-02-20"),
        ("Chronic Fatigue Syndrome", "2019-11-05"),
        ("POTS (Postural Orthostatic Tachycardia Syndrome)", "2021-03-12"),
        ("Small Fiber Neuropathy", "2022-07-18"),
        ("Gastroparesis", "2023-01-25"),
        ("MCAS (Mast Cell Activation Syndrome)", "2022-10-03"),
        ("Hypothyroidism", "2017-04-15"),
        ("Chronic Pain", "2018-09-10"),
        ("Sleep Disorders", "2016-08-22"),
    ]
    num_rows = len(diagnoses)
    num_cols = 2

    insert_index = 360  # End of diagnosis bullet list
    print(f"[DEBUG] Inserting blank paragraph at index: {insert_index}")

    # Insert a blank paragraph at index 360
    requests = [
        {
            "insertText": {
                "location": {"index": insert_index},
                "text": "\n"
            }
        }
    ]
    service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests}
    ).execute()

    # Now insert the table at index 361
    print(f"[DEBUG] Inserting table at index: {insert_index + 1}")
    requests = [
        {
            "insertTable": {
                "rows": num_rows,
                "columns": num_cols,
                "location": {"index": insert_index + 1}
            }
        }
    ]
    service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests}
    ).execute()

    doc = service.documents().get(documentId=document_id).execute()
    table = None
    for element in doc["body"]["content"]:
        if "table" in element:
            table = element["table"]
            break
    if not table:
        print("❌ Could not find the inserted table.")
        return

    requests = []
    for row_idx, row in enumerate(table["tableRows"]):
        for col_idx, cell in enumerate(row["tableCells"]):
            cell_start = cell["content"][0]["startIndex"]
            text = diagnoses[row_idx][col_idx]
            requests.append({
                "insertText": {
                    "location": {"index": cell_start + 1},
                    "text": text
                }
            })
    service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests}
    ).execute()
    print("Diagnosis table inserted after the diagnosis bullet list.")


def main():
    """Main function to create the Google Doc."""
    if not os.path.exists(MARKDOWN_FILE):
        print(f"Error: {MARKDOWN_FILE} not found!")
        return
    
    print("Authenticating with Google...")
    creds = authenticate_google()
    
    print("Creating Google Doc...")
    doc_id = create_google_doc(build('docs', 'v1', credentials=creds))
    
    if doc_id:
        print("\n✅ Success! Your medical document has been created.")
        print(f"📄 Document URL: https://docs.google.com/document/d/{doc_id}/edit")
        print("\nYou can now:")
        print("1. Open the document in Google Docs")
        print("2. Share it with others if needed")
        print("3. Edit and update as needed")
        
        insert_diagnoses_and_symptoms(build('docs', 'v1', credentials=creds), doc_id)
        insert_diagnosis_table(build('docs', 'v1', credentials=creds), doc_id)
        print("Diagnosis table inserted at the end of the document.")
    else:
        print("❌ Failed to create document.")


if __name__ == "__main__":
    creds = authenticate_google()
    service = build('docs', 'v1', credentials=creds)
    print(f"[DEBUG] Will update Google Doc with ID: {DOCUMENT_ID}")
    insert_diagnosis_table(service, DOCUMENT_ID)


if __name__ == '__main__':
    main() 