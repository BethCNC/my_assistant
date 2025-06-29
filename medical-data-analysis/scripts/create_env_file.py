#!/usr/bin/env python3
"""
Environment File Generator

This script creates a .env file for storing API keys and other sensitive information.
"""

import os
from getpass import getpass

def create_env_file(file_path=".env"):
    """Create a .env file with user input for API keys"""
    
    # Check if file already exists
    if os.path.exists(file_path):
        overwrite = input(f"{file_path} already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return False
    
    print("\n==== Setting up environment variables ====\n")
    
    # Get API keys securely
    openai_key = getpass("Enter your OpenAI API key: ")
    notion_token = getpass("Enter your Notion API token: ")
    
    # Database IDs (these are already configured in notion_field_mapping.json)
    env_content = f"""# API Keys
OPENAI_API_KEY={openai_key}
NOTION_TOKEN={notion_token}

# Database IDs
NOTION_MEDICAL_CALENDAR_DB=17b86edc-ae2c-81c1-83e0-e0a19a035932
NOTION_MEDICAL_TEAM_DB=17b86edc-ae2c-8155-8caa-fbb80647f6a9
NOTION_MEDICAL_CONDITIONS_DB=17b86edc-ae2c-8167-ba15-f9f03b49795e
NOTION_MEDICATIONS_DB=17b86edc-ae2c-81a7-b28a-e9fbcc7e7b62
NOTION_SYMPTOMS_DB=17b86edc-ae2c-81c6-9077-e55a68cf2438
"""
    
    try:
        # Write environment file
        with open(file_path, 'w') as f:
            f.write(env_content)
        
        # Set file permissions to be readable only by the owner
        os.chmod(file_path, 0o600)
        
        print(f"\n✅ Created {file_path} successfully!")
        print(f"   The file is set to be readable only by you.")
        print("\nTo use these environment variables:")
        print("1. For terminal sessions: Run 'source .env'")
        print("2. For scripts: The application will automatically load from this file\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    create_env_file() 