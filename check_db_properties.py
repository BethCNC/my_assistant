#!/usr/bin/env python3
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv('NOTION_TOKEN'))
db_id = os.getenv('TASKS_DATABASE_ID')

try:
    db = notion.databases.retrieve(database_id=db_id)
    print('Tasks Database Properties:')
    for prop_name, prop_data in db['properties'].items():
        print(f'  {prop_name}: {prop_data["type"]}')
        if prop_data["type"] in ["select", "status"]:
            options = prop_data.get(prop_data["type"], {}).get("options", [])
            if options:
                print(f'    Options: {[opt["name"] for opt in options]}')
except Exception as e:
    print(f'Error: {e}') 