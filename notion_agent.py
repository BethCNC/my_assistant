#!/usr/bin/env python3
"""
Notion AI Assistant - Your productivity agent for Notion workspace
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

console = Console()
notion = Client(auth=os.getenv("NOTION_TOKEN"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class NotionAgent:
    def __init__(self):
        self.default_db_id = os.getenv("DEFAULT_DATABASE_ID")
        
    def ai_suggest(self, task: str, context: str = "") -> str:
        """Get AI suggestions for organizing or completing tasks"""
        prompt = f"""
        You are a productivity assistant specializing in Notion workspace organization.
        
        Task: {task}
        Context: {context}
        
        Provide specific, actionable suggestions in 2-3 bullet points.
        Focus on Notion best practices for organization and productivity.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content

    def quick_capture(self, text: str, database_id: str = None) -> Dict:
        """Quickly capture ideas/tasks to Notion"""
        db_id = database_id or self.default_db_id
        
        # AI categorization
        category_prompt = f"""
        Categorize this note and suggest properties:
        "{text}"
        
        Return JSON with: {{"title": "...", "category": "task|idea|note", "priority": "high|medium|low", "tags": ["tag1", "tag2"]}}
        """
        
        ai_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": category_prompt}],
            max_tokens=150
        )
        
        try:
            suggested = json.loads(ai_response.choices[0].message.content)
        except:
            suggested = {"title": text[:50], "category": "note", "priority": "medium", "tags": []}

        # Create page in Notion
        page_data = {
            "parent": {"database_id": db_id},
            "properties": {
                "Name": {"title": [{"text": {"content": suggested["title"]}}]},
                "Category": {"select": {"name": suggested["category"]}},
                "Priority": {"select": {"name": suggested["priority"]}},
                "Created": {"date": {"start": datetime.now().isoformat()}}
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": text}}]
                    }
                }
            ]
        }
        
        page = notion.pages.create(**page_data)
        return {"page": page, "suggested": suggested}

    def weekly_review(self) -> None:
        """Generate weekly productivity review"""
        # Get recent pages
        last_week = (datetime.now() - timedelta(days=7)).isoformat()
        
        results = notion.databases.query(
            database_id=self.default_db_id,
            filter={
                "property": "Created",
                "date": {"after": last_week}
            }
        )
        
        # AI analysis
        pages_summary = "\n".join([
            f"- {page['properties']['Name']['title'][0]['text']['content']}"
            for page in results['results'][:10]
        ])
        
        analysis_prompt = f"""
        Weekly productivity review based on Notion activity:
        
        {pages_summary}
        
        Provide:
        1. Key accomplishments
        2. Patterns you notice
        3. Suggestions for next week
        4. Areas needing better organization
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=500
        )
        
        console.print(f"\n[bold blue]Weekly Review[/bold blue]")
        console.print(response.choices[0].message.content)

    def smart_search(self, query: str) -> None:
        """AI-enhanced search across Notion"""
        # Basic search
        results = notion.search(query=query, page_size=10)
        
        if not results['results']:
            console.print(f"[yellow]No direct matches for '{query}'[/yellow]")
            
            # AI suggestion for better search terms
            suggestion = self.ai_suggest(
                f"Suggest better search terms for: {query}",
                "User is searching their Notion workspace"
            )
            console.print(f"\n[dim]AI Suggestion:[/dim] {suggestion}")
            return
        
        table = Table(title=f"Search Results: {query}")
        table.add_column("Title", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("URL", style="blue")
        
        for item in results['results']:
            title = "Untitled"
            if item['object'] == 'page' and item.get('properties', {}).get('Name'):
                title = item['properties']['Name']['title'][0]['text']['content']
            elif item.get('title'):
                title = item['title'][0]['text']['content']
                
            table.add_row(
                title[:50],
                item['object'],
                item['url']
            )
        
        console.print(table)

@click.group()
def cli():
    """Notion AI Assistant - Your productivity companion"""
    pass

@cli.command()
@click.argument('text')
@click.option('--database-id', help='Specific database ID to use')
def capture(text, database_id):
    """Quickly capture ideas/tasks with AI categorization"""
    agent = NotionAgent()
    result = agent.quick_capture(text, database_id)
    
    console.print(f"[green]✅ Captured:[/green] {result['suggested']['title']}")
    console.print(f"[dim]Category: {result['suggested']['category']} | Priority: {result['suggested']['priority']}[/dim]")

@cli.command()
@click.argument('query')
def search(query):
    """AI-enhanced search across your Notion workspace"""
    agent = NotionAgent()
    agent.smart_search(query)

@cli.command()
@click.argument('task')
@click.option('--context', default='', help='Additional context for suggestions')
def suggest(task, context):
    """Get AI suggestions for organizing or completing tasks"""
    agent = NotionAgent()
    suggestion = agent.ai_suggest(task, context)
    console.print(f"[blue]💡 AI Suggestion:[/blue]\n{suggestion}")

@cli.command()
def review():
    """Generate weekly productivity review"""
    agent = NotionAgent()
    agent.weekly_review()

@cli.command()
def setup():
    """Interactive setup for API keys and database"""
    console.print("[bold blue]Setting up Notion AI Assistant[/bold blue]\n")
    
    # Check if config file exists
    if not os.path.exists('.env'):
        console.print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Notion AI Assistant Configuration\n")
            f.write("NOTION_TOKEN=\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("DEFAULT_DATABASE_ID=\n")
    
    console.print("Please add your API keys to the .env file:")
    console.print("1. NOTION_TOKEN - Get from https://www.notion.so/my-integrations")
    console.print("2. OPENAI_API_KEY - Get from https://platform.openai.com/api-keys")
    console.print("3. DEFAULT_DATABASE_ID - The database where you want to capture quick notes")

if __name__ == '__main__':
    cli() 