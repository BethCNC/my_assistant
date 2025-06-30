import os
import sys
from typing import List, Dict, Any
from google.cloud import firestore
from google.api_core.exceptions import GoogleAPIError

# Usage: Set GOOGLE_APPLICATION_CREDENTIALS to your service account key JSON
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

FIRESTORE_PROJECT = os.getenv("FIRESTORE_PROJECT")  # Optional: set your project explicitly

# Initialize Firestore client
if FIRESTORE_PROJECT:
    db = firestore.Client(project=FIRESTORE_PROJECT)
else:
    db = firestore.Client()

def upload_health_events(user_id: str, health_events: List[Dict[str, Any]]) -> int:
    """
    Upload a list of health events to Firestore under users/{userId}/healthEvents.
    Returns the number of successful uploads.
    """
    success = 0
    for event in health_events:
        try:
            # Use event['id'] if present, else auto-generate
            doc_ref = db.collection("users").document(user_id).collection("healthEvents").document(event.get("id") or None)
            doc_ref.set(event)
            success += 1
        except GoogleAPIError as e:
            print(f"[Firestore] Failed to upload event: {e}")
    return success

def upload_entities(user_id: str, entity_type: str, entities: List[Dict[str, Any]]):
    """
    Generic uploader for other entity types (e.g., medications, symptoms).
    """
    for entity in entities:
        try:
            doc_ref = db.collection("users").document(user_id).collection(entity_type).document(entity.get("id") or None)
            doc_ref.set(entity)
        except GoogleAPIError as e:
            print(f"[Firestore] Failed to upload {entity_type}: {e}")

if __name__ == "__main__":
    # Example CLI usage: python firestore_upload.py <user_id> <json_file>
    import json
    if len(sys.argv) != 3:
        print("Usage: python firestore_upload.py <user_id> <health_events.json>")
        sys.exit(1)
    user_id = sys.argv[1]
    json_file = sys.argv[2]
    with open(json_file, "r") as f:
        events = json.load(f)
    if not isinstance(events, list):
        print("JSON file must contain a list of health event dicts.")
        sys.exit(1)
    uploaded = upload_health_events(user_id, events)
    print(f"Uploaded {uploaded} health events to Firestore for user {user_id}.") 