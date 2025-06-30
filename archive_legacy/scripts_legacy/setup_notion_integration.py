#!/usr/bin/env python3
"""
Notion Integration Setup Script

This script helps you set up your Notion integration by:
1. Collecting your API keys
2. Updating your configuration file
3. Verifying your configuration
"""

import json
import os
from getpass import getpass
import subprocess
import sys

CONFIG_FILE = "config/notion_config.json"

def load_config():
    """Load the current configuration."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return None

def save_config(config):
    """Save the updated configuration."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config file: {str(e)}")
        return False

def collect_api_keys():
    """Collect API keys from the user."""
    print("\n=== API Key Collection ===")
    print("\nTo use the Notion integration, you need to provide two API keys:")
    
    # Notion API token
    print("\n1. Notion API Token")
    print("   You can get this at https://www.notion.so/my-integrations")
    print("   If you haven't created an integration yet:")
    print("   - Go to https://www.notion.so/my-integrations")
    print("   - Click 'New integration'")
    print("   - Name it 'Medical Data Integration'")
    print("   - Select your workspace")
    print("   - Copy the 'Internal Integration Token'")
    token = getpass("Enter your Notion API token (starts with 'secret_'): ")
    
    # OpenAI API key
    print("\n2. OpenAI API Key")
    print("   You can get this at https://platform.openai.com/api-keys")
    openai_key = getpass("Enter your OpenAI API key (starts with 'sk-'): ")
    
    return token, openai_key

def update_config_with_keys(config, token, openai_key):
    """Update the configuration with the provided API keys."""
    if not config:
        return False
        
    try:
        config["notion"]["token"] = token
        config["openai"]["api_key"] = openai_key
        return True
    except Exception as e:
        print(f"Error updating config: {str(e)}")
        return False

def verify_configuration():
    """Run the verification script to check the configuration."""
    print("\n=== Verifying Configuration ===")
    mapping_file = "config/notion_field_mapping.json"
    
    try:
        result = subprocess.run(
            [sys.executable, "verify_notion_config.py", "--config", CONFIG_FILE, "--mapping", mapping_file],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode == 0 and "✅ Configuration verified successfully!" in result.stdout:
            return True
        else:
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error running verification: {str(e)}")
        return False

def main():
    # Ensure config directory exists
    os.makedirs("config", exist_ok=True)
    
    # Load existing config
    config = load_config()
    if not config:
        print("Unable to load configuration file. Please check if it exists.")
        return
    
    # Collect API keys
    token, openai_key = collect_api_keys()
    
    # Update config with API keys
    if update_config_with_keys(config, token, openai_key) and save_config(config):
        print("\n✅ Configuration updated successfully!")
    else:
        print("\n❌ Failed to update configuration.")
        return
    
    # Verify configuration
    if verify_configuration():
        print("\n✅ Your Notion integration is ready!")
        print("\nTo sync your medical data to Notion, run:")
        print("  ./run_notion_sync.sh")
    else:
        print("\n❌ Configuration verification failed.")
        print("Please fix the issues indicated above and try again.")

if __name__ == "__main__":
    main() 