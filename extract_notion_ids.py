#!/usr/bin/env python3
"""
Script to extract all Notion database IDs from Beth's workspace
Run this to automatically find and list all your database IDs for the .env file
"""

import os
from notion_client import Client
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()

console = Console()

def extract_database_ids():
    """Extract all database IDs from Beth's Notion workspace"""
    
    # Use existing token from .env
    token = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
    
    if not token:
        console.print("[red]❌ No Notion token found in .env file[/red]")
        console.print("Add NOTION_TOKEN=your_token_here to your .env file")
        return
    
    notion = Client(auth=token)
    
    try:
        console.print(Panel.fit(
            "[bold blue]🔍 Extracting Database IDs from Your Notion Workspace[/bold blue]",
            border_style="blue"
        ))
        
        # Search for databases
        search_results = notion.search(
            filter={"value": "database", "property": "object"}
        )
        
        if not search_results.get('results'):
            console.print("[yellow]⚠️ No databases found. Check your integration permissions.[/yellow]")
            return
        
        # Create table for results
        table = Table(title="Your Notion Databases")
        table.add_column("Database Name", style="cyan", no_wrap=True)
        table.add_column("Database ID", style="green")
        table.add_column("Suggested Env Variable", style="yellow")
        
        # Map common database names to env variables
        env_mapping = {
            "tasks": "TASKS_DATABASE_ID",
            "task": "TASKS_DATABASE_ID", 
            "projects": "PROJECTS_DATABASE_ID",
            "project": "PROJECTS_DATABASE_ID",
            "notes": "NOTES_DATABASE_ID",
            "note": "NOTES_DATABASE_ID",
            "clients": "CLIENTS_DATABASE_ID",
            "client": "CLIENTS_DATABASE_ID",
            "medical calendar": "HEALTH_CALENDAR_DATABASE_ID",
            "health": "HEALTH_CALENDAR_DATABASE_ID",
            "brand assets": "BRAND_ASSETS_DATABASE_ID",
            "assets": "BRAND_ASSETS_DATABASE_ID",
            "chat": "CHAT_MEMORY_DATABASE_ID",
            "conversations": "CHAT_MEMORY_DATABASE_ID",
            "memory": "CHAT_MEMORY_DATABASE_ID"
        }
        
        databases = []
        for result in search_results['results']:
            if result['object'] == 'database':
                name = result.get('title', [{}])[0].get('plain_text', 'Untitled')
                db_id = result['id']
                
                # Suggest env variable name
                suggested_var = "DATABASE_ID"
                for keyword, var_name in env_mapping.items():
                    if keyword.lower() in name.lower():
                        suggested_var = var_name
                        break
                
                databases.append((name, db_id, suggested_var))
                table.add_row(name, db_id, suggested_var)
        
        console.print(table)
        
        # Generate .env content
        console.print(f"\n[bold green]📝 Copy this to your .env file:[/bold green]")
        console.print(Panel(
            generate_env_content(databases),
            title="Updated .env Content",
            border_style="green"
        ))
        
        console.print(f"\n[dim]💡 Found {len(databases)} databases total[/dim]")
        console.print(f"[dim]Make sure to grant database access to your Notion integration![/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[dim]Check that your Notion token is valid and has the right permissions[/dim]")

def generate_env_content(databases):
    """Generate .env file content with discovered databases"""
    content = """# === CORE API KEYS ===
NOTION_TOKEN=your_notion_token_here
OPENAI_API_KEY=your_openai_key_here  
FIGMA_ACCESS_TOKEN=your_figma_token_here

# === NOTION DATABASE IDS ===
# Found in your workspace:
"""
    
    for name, db_id, var_name in databases:
        content += f"{var_name}={db_id}  # {name}\n"
    
    content += """
# === GIT REPOSITORIES ===
GIT_REPOS_PATH=/Users/bethcartrette/REPOS
MAIN_PROJECTS_PATH=/Users/bethcartrette/REPOS

# === MEMORY SETTINGS ===
MEMORY_DB_PATH=./chat_memory.db
CONTEXT_HISTORY_DAYS=30
"""
    
    return content

if __name__ == "__main__":
    extract_database_ids() 