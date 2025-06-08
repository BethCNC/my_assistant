#!/usr/bin/env python3
"""
Beth's Personal Notion AI Assistant
Designed for PARA method, business CRM, health management, and ADHD-friendly workflows
"""

import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

console = Console()
notion = Client(auth=os.getenv("NOTION_TOKEN"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class BethNotionAgent:
    def __init__(self):
        # Beth's core database IDs (will be configured in setup)
        self.tasks_db_id = os.getenv("TASKS_DATABASE_ID")
        self.projects_db_id = os.getenv("PROJECTS_DATABASE_ID") 
        self.notes_db_id = os.getenv("NOTES_DATABASE_ID")
        self.clients_db_id = os.getenv("CLIENTS_DATABASE_ID")
        self.health_calendar_db_id = os.getenv("HEALTH_CALENDAR_DATABASE_ID")
        
        # Load Beth's system instructions for AI context
        self.system_context = self._load_system_context()
        
    def _load_system_context(self) -> str:
        """Load Beth's Notion system instructions for AI context"""
        try:
            with open('beth_master_notion_instructions.md', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "PARA method with business CRM and health management focus"

    def ai_suggest_with_context(self, task: str, context: str = "") -> str:
        """AI suggestions with Beth's system context and ADHD-friendly approach"""
        prompt = f"""
        You are Beth's personal productivity assistant, specializing in her PARA-method Notion workspace.
        
        SYSTEM CONTEXT:
        {self.system_context}
        
        CURRENT REQUEST:
        Task: {task}
        Additional Context: {context}
        
        Provide 2-3 specific, actionable suggestions that:
        - Reduce cognitive load (ADHD-friendly)
        - Work with her PARA method (Projects/Areas/Notes/Archive)
        - Consider her business operations and health management needs
        - Suggest which specific database/view to use
        - Focus on immediate next actions, not overwhelming planning
        
        Keep suggestions practical and energy-conscious.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        return response.choices[0].message.content

    def smart_capture(self, text: str, capture_type: str = "auto") -> Dict:
        """ADHD-friendly quick capture with AI categorization for Beth's system"""
        
        # AI analysis for Beth's specific workflow
        analysis_prompt = f"""
        Analyze this capture for Beth's PARA Notion system:
        "{text}"
        
        Determine:
        1. Database: "tasks" (actionable), "notes" (reference), "health" (medical), or "business" (client-related)
        2. Category: For tasks: "Inbox"|"Next Action"|"Someday Maybe". For notes: content type from her system
        3. Priority: "High"|"Medium"|"Low" based on urgency and energy required
        4. Life Area: "Personal"|"Work"|"Health" 
        5. Suggested title (max 50 chars)
        6. Energy level: "High"|"Medium"|"Low" (cognitive demand)
        
        Return JSON: {{"database": "...", "category": "...", "priority": "...", "life_area": "...", "title": "...", "energy": "..."}}
        """
        
        ai_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=200
        )
        
        try:
            analysis = json.loads(ai_response.choices[0].message.content)
        except:
            # Fallback for parsing errors
            analysis = {
                "database": "tasks",
                "category": "Inbox", 
                "priority": "Medium",
                "life_area": "Personal",
                "title": text[:50],
                "energy": "Medium"
            }

        # Route to appropriate database
        if analysis["database"] == "tasks":
            return self._create_task(text, analysis)
        elif analysis["database"] == "notes":
            return self._create_note(text, analysis)
        elif analysis["database"] == "health":
            return self._create_health_item(text, analysis)
        else:
            return self._create_task(text, analysis)  # Default to tasks

    def _create_task(self, text: str, analysis: Dict) -> Dict:
        """Create task in Beth's Tasks database with proper properties"""
        page_data = {
            "parent": {"database_id": self.tasks_db_id},
            "properties": {
                "Task": {"title": [{"text": {"content": analysis["title"]}}]},
                "Status": {"select": {"name": analysis["category"]}},
                "Priority": {"select": {"name": analysis["priority"]}},
                "Life Area": {"select": {"name": analysis["life_area"]}},
                "Energy Level": {"select": {"name": analysis["energy"]}},
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
        
        try:
            page = notion.pages.create(**page_data)
            return {"success": True, "page": page, "analysis": analysis, "type": "task"}
        except Exception as e:
            return {"success": False, "error": str(e), "analysis": analysis}

    def _create_note(self, text: str, analysis: Dict) -> Dict:
        """Create note in Beth's Notes database"""
        page_data = {
            "parent": {"database_id": self.notes_db_id},
            "properties": {
                "Name": {"title": [{"text": {"content": analysis["title"]}}]},
                "Type": {"select": {"name": "Quick Note"}},
                "Life Area": {"select": {"name": analysis["life_area"]}},
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
        
        try:
            page = notion.pages.create(**page_data)
            return {"success": True, "page": page, "analysis": analysis, "type": "note"}
        except Exception as e:
            return {"success": False, "error": str(e), "analysis": analysis}

    def daily_command_center(self) -> None:
        """Marie Poulin-inspired ADHD-friendly daily dashboard"""
        console.print(Panel.fit(
            "[bold blue]🧠 Beth's Daily Command Center[/bold blue]\n"
            "[dim]ADHD-optimized productivity dashboard[/dim]",
            border_style="blue"
        ))
        
        # Get today's focus tasks
        today = date.today().isoformat()
        
        try:
            # Inbox items needing processing
            inbox_results = notion.databases.query(
                database_id=self.tasks_db_id,
                filter={"property": "Status", "select": {"equals": "Inbox"}},
                page_size=10
            )
            
            # Next Actions ready to work on
            next_actions = notion.databases.query(
                database_id=self.tasks_db_id,
                filter={"property": "Status", "select": {"equals": "Next Action"}},
                page_size=5
            )
            
            # Display Inbox (limit to reduce overwhelm)
            if inbox_results['results']:
                console.print(f"\n[yellow]📥 Inbox ({len(inbox_results['results'])} items)[/yellow]")
                for i, task in enumerate(inbox_results['results'][:3]):  # Show only first 3
                    title = task['properties']['Task']['title'][0]['text']['content']
                    console.print(f"  {i+1}. {title}")
                if len(inbox_results['results']) > 3:
                    console.print(f"  ... and {len(inbox_results['results']) - 3} more")
                console.print(f"[dim]💡 Process these during your 10-minute morning routine[/dim]")
            
            # Display Next Actions (ADHD-friendly limit of 3)
            if next_actions['results']:
                console.print(f"\n[green]🎯 Ready to Work On[/green]")
                for i, task in enumerate(next_actions['results'][:3]):
                    title = task['properties']['Task']['title'][0]['text']['content']
                    priority = task['properties'].get('Priority', {}).get('select', {}).get('name', 'Medium')
                    energy = task['properties'].get('Energy Level', {}).get('select', {}).get('name', 'Medium')
                    console.print(f"  {i+1}. {title} [{priority} priority, {energy} energy]")
            else:
                console.print(f"\n[green]🎯 No Next Actions ready[/green]")
                console.print(f"[dim]Process your inbox to identify next actions![/dim]")
                
        except Exception as e:
            console.print(f"[red]Error accessing tasks: {e}[/red]")
            console.print("[dim]Make sure your TASKS_DATABASE_ID is configured correctly[/dim]")

    def business_dashboard(self) -> None:
        """Client and project overview for business operations"""
        console.print(Panel.fit(
            "[bold cyan]💼 Business Command Center[/bold cyan]\n"
            "[dim]Client projects and operations overview[/dim]",
            border_style="cyan"
        ))
        
        try:
            # Active projects
            active_projects = notion.databases.query(
                database_id=self.projects_db_id,
                filter={"property": "Status", "select": {"equals": "In Progress"}},
                page_size=5
            )
            
            if active_projects['results']:
                console.print(f"\n[cyan]🚀 Active Projects[/cyan]")
                for project in active_projects['results']:
                    name = project['properties']['Name']['title'][0]['text']['content']
                    console.print(f"  • {name}")
            
            # Quick business insights
            console.print(f"\n[dim]💡 Quick Actions:[/dim]")
            console.print(f"  • Check invoices due this week")
            console.print(f"  • Review client communication status")
            console.print(f"  • Update project progress")
            
        except Exception as e:
            console.print(f"[red]Error accessing projects: {e}[/red]")

    def health_dashboard(self) -> None:
        """Health management overview for medical tracking"""
        console.print(Panel.fit(
            "[bold green]🏥 Health Command Center[/bold green]\n"
            "[dim]Medical appointments and health tracking[/dim]",
            border_style="green"
        ))
        
        # Get upcoming week
        next_week = (datetime.now() + timedelta(days=7)).isoformat()
        
        try:
            upcoming_health = notion.databases.query(
                database_id=self.health_calendar_db_id,
                filter={
                    "property": "Date",
                    "date": {"before": next_week}
                },
                page_size=5
            )
            
            if upcoming_health['results']:
                console.print(f"\n[green]📅 Upcoming Health Items[/green]")
                for item in upcoming_health['results']:
                    name = item['properties']['Name']['title'][0]['text']['content']
                    console.print(f"  • {name}")
            
            console.print(f"\n[dim]💡 Health Actions:[/dim]")
            console.print(f"  • Log symptoms if needed")
            console.print(f"  • Prepare for upcoming appointments") 
            console.print(f"  • Review medication schedule")
            
        except Exception as e:
            console.print(f"[red]Error accessing health calendar: {e}[/red]")

    def weekly_review_enhanced(self) -> None:
        """Expert-informed weekly review with PARA focus"""
        console.print(Panel.fit(
            "[bold magenta]📊 Weekly Review - PARA Method[/bold magenta]\n"
            "[dim]August Bradley & Marie Poulin inspired analysis[/dim]",
            border_style="magenta"
        ))
        
        last_week = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Analyze task completion by Life Area
        try:
            completed_tasks = notion.databases.query(
                database_id=self.tasks_db_id,
                filter={
                    "and": [
                        {"property": "Status", "select": {"equals": "Completed"}},
                        {"property": "Created", "date": {"after": last_week}}
                    ]
                }
            )
            
            # Group by Life Area for PARA analysis
            life_areas = {}
            for task in completed_tasks['results']:
                area = task['properties'].get('Life Area', {}).get('select', {}).get('name', 'Uncategorized')
                if area not in life_areas:
                    life_areas[area] = []
                life_areas[area].append(task['properties']['Task']['title'][0]['text']['content'])
            
            console.print(f"\n[magenta]🎯 Accomplishments by Life Area[/magenta]")
            for area, tasks in life_areas.items():
                console.print(f"\n[bold]{area}:[/bold]")
                for task in tasks[:3]:  # Limit to reduce overwhelm
                    console.print(f"  ✅ {task}")
                if len(tasks) > 3:
                    console.print(f"  ... and {len(tasks) - 3} more")
            
            # AI-powered weekly insight
            tasks_summary = "\n".join([
                f"- {area}: {len(tasks)} tasks completed"
                for area, tasks in life_areas.items()
            ])
            
            analysis_prompt = f"""
            Weekly review for Beth's ADHD-friendly PARA system:
            
            Completed tasks by area:
            {tasks_summary}
            
            Provide a brief, encouraging weekly review focusing on:
            1. Key patterns in her productivity
            2. One specific suggestion for next week
            3. Energy management insights
            
            Keep it concise and motivating, not overwhelming.
            """
            
            ai_response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=300
            )
            
            console.print(f"\n[blue]🤖 AI Insights[/blue]")
            console.print(ai_response.choices[0].message.content)
            
        except Exception as e:
            console.print(f"[red]Error generating weekly review: {e}[/red]")

    def process_inbox(self) -> None:
        """ADHD-friendly inbox processing with 10-minute timer"""
        console.print(Panel.fit(
            "[bold yellow]📥 Inbox Processing[/bold yellow]\n"
            "[dim]ADHD-friendly 10-minute max session[/dim]",
            border_style="yellow"
        ))
        
        try:
            inbox_items = notion.databases.query(
                database_id=self.tasks_db_id,
                filter={"property": "Status", "select": {"equals": "Inbox"}},
                page_size=10
            )
            
            if not inbox_items['results']:
                console.print("[green]🎉 Inbox is empty! Great job![/green]")
                return
            
            console.print(f"Found {len(inbox_items['results'])} items to process")
            console.print("[dim]For each item: Next Action, Someday Maybe, or Delete[/dim]\n")
            
            processed = 0
            for item in inbox_items['results'][:5]:  # Limit to 5 items max
                title = item['properties']['Task']['title'][0]['text']['content']
                console.print(f"📝 {title}")
                
                # AI suggestion for categorization
                suggestion = self.ai_suggest_with_context(
                    f"How should I categorize this inbox item: '{title}'",
                    "Processing inbox with 2-minute rule and energy consideration"
                )
                console.print(f"[dim]💡 AI suggests: {suggestion}[/dim]")
                
                action = Prompt.ask(
                    "Action",
                    choices=["next", "someday", "skip", "done"],
                    default="skip"
                )
                
                if action == "next":
                    self._update_task_status(item['id'], "Next Action")
                    console.print("[green]✅ Moved to Next Action[/green]")
                elif action == "someday":
                    self._update_task_status(item['id'], "Someday Maybe")
                    console.print("[blue]📅 Moved to Someday Maybe[/blue]")
                elif action == "done":
                    break
                
                processed += 1
                console.print()
            
            console.print(f"[green]Processed {processed} items in your 10-minute session![/green]")
            
        except Exception as e:
            console.print(f"[red]Error processing inbox: {e}[/red]")

    def _update_task_status(self, page_id: str, new_status: str) -> bool:
        """Update task status in Notion"""
        try:
            notion.pages.update(
                page_id=page_id,
                properties={"Status": {"select": {"name": new_status}}}
            )
            return True
        except Exception as e:
            console.print(f"[red]Error updating status: {e}[/red]")
            return False

@click.group()
def cli():
    """Beth's Personal Notion AI Assistant - PARA Method + Business + Health"""
    pass

@cli.command()
@click.argument('text')
@click.option('--type', help='Force type: task, note, health, business')
def capture(text, type):
    """Smart capture with AI categorization for Beth's PARA system"""
    agent = BethNotionAgent()
    result = agent.smart_capture(text, type or "auto")
    
    if result["success"]:
        analysis = result["analysis"]
        console.print(f"[green]✅ Captured as {result['type']}:[/green] {analysis['title']}")
        console.print(f"[dim]→ {analysis['database']} | {analysis['category']} | {analysis['life_area']} | {analysis['energy']} energy[/dim]")
    else:
        console.print(f"[red]❌ Error: {result['error']}[/red]")
        console.print(f"[dim]Try: python notion_agent.py setup[/dim]")

@cli.command()
def daily():
    """Open Beth's ADHD-friendly daily command center"""
    agent = BethNotionAgent()
    agent.daily_command_center()

@cli.command()
def business():
    """Business operations dashboard - clients and projects"""
    agent = BethNotionAgent()
    agent.business_dashboard()

@cli.command()
def health():
    """Health management dashboard - appointments and tracking"""
    agent = BethNotionAgent()
    agent.health_dashboard()

@cli.command()
def inbox():
    """Process inbox items with ADHD-friendly 10-minute sessions"""
    agent = BethNotionAgent()
    agent.process_inbox()

@cli.command()
def review():
    """Weekly review with PARA method and expert insights"""
    agent = BethNotionAgent()
    agent.weekly_review_enhanced()

@cli.command()
@click.argument('task')
@click.option('--context', default='', help='Additional context')
def suggest(task, context):
    """Get AI suggestions tailored to Beth's PARA system and workflows"""
    agent = BethNotionAgent()
    suggestion = agent.ai_suggest_with_context(task, context)
    console.print(f"[blue]💡 Personalized Suggestion:[/blue]\n{suggestion}")

@cli.command()
def setup():
    """Setup Beth's personalized Notion AI assistant"""
    console.print(Panel.fit(
        "[bold blue]🧠 Beth's Notion AI Assistant Setup[/bold blue]\n"
        "[dim]Configuring for PARA method + Business + Health[/dim]",
        border_style="blue"
    ))
    
    if not os.path.exists('.env'):
        console.print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Beth's Notion AI Assistant Configuration\n")
            f.write("NOTION_TOKEN=\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("# Beth's Core Database IDs\n")
            f.write("TASKS_DATABASE_ID=\n")
            f.write("PROJECTS_DATABASE_ID=\n")
            f.write("NOTES_DATABASE_ID=\n")
            f.write("CLIENTS_DATABASE_ID=\n")
            f.write("HEALTH_CALENDAR_DATABASE_ID=\n")
    
    console.print("\n[bold]Required API Keys:[/bold]")
    console.print("1. NOTION_TOKEN - Your integration token")
    console.print("2. OPENAI_API_KEY - Your OpenAI API key")
    
    console.print("\n[bold]Required Database IDs:[/bold]")
    console.print("3. TASKS_DATABASE_ID - Your main Tasks database")
    console.print("4. PROJECTS_DATABASE_ID - Your Projects database")
    console.print("5. NOTES_DATABASE_ID - Your Notes database")
    console.print("6. CLIENTS_DATABASE_ID - Your Clients database")
    console.print("7. HEALTH_CALENDAR_DATABASE_ID - Your Medical Calendar database")
    
    console.print(f"\n[dim]💡 Find database IDs in the URL when viewing your databases[/dim]")
    console.print(f"[dim]💡 Database permissions must be granted to your Notion integration[/dim]")

if __name__ == '__main__':
    cli() 