#!/usr/bin/env python3
"""
Beth's Unified Personal AI Agent
Integrates: Notion (data), Figma (design), Git (code), Chat Memory (context), Life Management
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.columns import Columns
import subprocess
import requests
from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

console = Console()

class BethUnifiedAgent:
    def __init__(self):
        # Core services
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.figma_token = os.getenv("FIGMA_ACCESS_TOKEN")
        
        # Database connections
        self._init_memory_db()
        self._init_notion_databases()
        
        # Agent context
        self.conversation_history = []
        self.current_context = {}
        
    def _init_memory_db(self):
        """Initialize SQLite database for conversation memory and context"""
        self.memory_db_path = Path("agent_memory.db")
        self.memory_conn = sqlite3.connect(self.memory_db_path)
        
        # Create tables for memory management
        self.memory_conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                context_tags TEXT,
                importance_score INTEGER DEFAULT 5
            );
            
            CREATE TABLE IF NOT EXISTS context_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_key TEXT UNIQUE NOT NULL,
                context_value TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                relevance_score INTEGER DEFAULT 5
            );
            
            CREATE TABLE IF NOT EXISTS project_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_type TEXT,
                status TEXT,
                files_tracked TEXT,
                last_activity TEXT,
                metadata TEXT
            );
            
            CREATE TABLE IF NOT EXISTS life_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                impact_level INTEGER DEFAULT 3,
                related_projects TEXT
            );
        """)
        self.memory_conn.commit()

    def _init_notion_databases(self):
        """Initialize Notion database connections"""
        self.databases = {
            'tasks': os.getenv("TASKS_DATABASE_ID"),
            'projects': os.getenv("PROJECTS_DATABASE_ID"),
            'notes': os.getenv("NOTES_DATABASE_ID"),
            'clients': os.getenv("CLIENTS_DATABASE_ID"),
            'health': os.getenv("HEALTH_CALENDAR_DATABASE_ID"),
            'brand_assets': os.getenv("BRAND_ASSETS_DATABASE_ID"),
            'chat_memory': os.getenv("CHAT_MEMORY_DATABASE_ID")  # New memory database
        }

    def remember_conversation(self, user_input: str, agent_response: str, context_tags: List[str] = None, importance: int = 5):
        """Store conversation in memory for future context"""
        tags_json = json.dumps(context_tags or [])
        timestamp = datetime.now().isoformat()
        
        self.memory_conn.execute("""
            INSERT INTO conversations (timestamp, user_input, agent_response, context_tags, importance_score)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, user_input, agent_response, tags_json, importance))
        self.memory_conn.commit()

    def update_context(self, key: str, value: Any, relevance: int = 5):
        """Update persistent context memory"""
        timestamp = datetime.now().isoformat()
        value_json = json.dumps(value) if not isinstance(value, str) else value
        
        self.memory_conn.execute("""
            INSERT OR REPLACE INTO context_memory (context_key, context_value, last_updated, relevance_score)
            VALUES (?, ?, ?, ?)
        """, (key, value_json, timestamp, relevance))
        self.memory_conn.commit()

    def get_relevant_context(self, query: str, limit: int = 3) -> str:
        """Retrieve relevant conversation history and context for current query"""
        # Get recent important conversations
        recent_convos = self.memory_conn.execute("""
            SELECT user_input, agent_response, context_tags, timestamp
            FROM conversations 
            WHERE importance_score >= 7 OR timestamp > ?
            ORDER BY timestamp DESC LIMIT ?
        """, ((datetime.now() - timedelta(days=7)).isoformat(), limit)).fetchall()
        
        # Get relevant context
        context_data = self.memory_conn.execute("""
            SELECT context_key, context_value, last_updated
            FROM context_memory
            WHERE relevance_score >= 5
            ORDER BY last_updated DESC
        """).fetchall()
        
        # Format as string for AI prompt
        context_str = ""
        if recent_convos:
            context_str += f"Recent: {recent_convos[0][0] if recent_convos[0] else ''}"
        if context_data:
            context_str += f" | Context: {list(context_data)[:2]}"
        return context_str[:200]  # Limit length

    # === NOTION INTEGRATION ===
    
    def notion_smart_capture(self, text: str, context: str = "") -> Dict:
        """Enhanced capture with memory context"""
        relevant_context = self.get_relevant_context(text, limit=3)  # Limit context
        
        analysis_prompt = f"""Analyze: "{text}"

Return ONLY this JSON format:
{{"database": "tasks", "title": "{text[:50]}", "priority": "Medium", "status": "In Inbox", "life_area": "Personal"}}"""
        
        ai_response = self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=300
        )
        
        try:
            analysis = json.loads(ai_response.choices[0].message.content)
            result = self._create_notion_item(text, analysis)
            
            # Remember this interaction
            self.remember_conversation(
                text, 
                f"Captured to {analysis.get('database', 'unknown')} with context analysis",
                context_tags=[analysis.get('database'), analysis.get('category')],
                importance=analysis.get('priority_score', 5)
            )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_notion_item(self, text: str, analysis: Dict) -> Dict:
        """Create item in appropriate Notion database"""
        db_id = self.databases.get(analysis.get('database', 'tasks'))
        if not db_id:
            return {"success": False, "error": f"Database {analysis.get('database')} not configured"}
        
        # Create page based on database type
        page_data = {
            "parent": {"database_id": db_id},
            "properties": self._build_notion_properties(analysis),
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}
                }
            ]
        }
        
        try:
            page = self.notion.pages.create(**page_data)
            return {"success": True, "page": page, "analysis": analysis}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_notion_properties(self, analysis: Dict) -> Dict:
        """Build Notion properties based on analysis and database type"""
        db_type = analysis.get('database', 'tasks')
        
        base_props = {
            "Task name": {"title": [{"text": {"content": analysis.get('title', 'Untitled')}}]}
        }
        
        if db_type == 'tasks':
            base_props.update({
                "Status": {"status": {"name": analysis.get('status', 'In Inbox')}},
                "Priority": {"select": {"name": analysis.get('priority', 'Medium')}}
                # Note: Life Area is a relation field, would need different handling
            })
        elif db_type == 'projects':
            base_props.update({
                "Status": {"select": {"name": analysis.get('status', 'Planning')}},
                "Type": {"select": {"name": analysis.get('project_type', 'Personal')}}
            })
        
        return base_props

    # === FIGMA INTEGRATION ===
    
    def figma_get_recent_files(self, team_id: str = None) -> List[Dict]:
        """Get recent Figma files"""
        if not self.figma_token:
            return {"error": "Figma token not configured"}
        
        headers = {"X-Figma-Token": self.figma_token}
        response = requests.get("https://api.figma.com/v1/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return {"error": f"Figma API error: {response.status_code}"}

    def figma_track_design_changes(self, file_key: str, project_name: str = None):
        """Track changes in a specific Figma file"""
        if not self.figma_token:
            return {"error": "Figma token not configured"}
        
        headers = {"X-Figma-Token": self.figma_token}
        response = requests.get(f"https://api.figma.com/v1/files/{file_key}", headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            
            # Store/update project context
            self.memory_conn.execute("""
                INSERT OR REPLACE INTO project_context 
                (project_name, project_type, status, files_tracked, last_activity, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_name or file_data.get('name', 'Unknown'),
                'design',
                'active',
                json.dumps([file_key]),
                datetime.now().isoformat(),
                json.dumps(file_data)
            ))
            self.memory_conn.commit()
            
            return {"success": True, "file_data": file_data}
        
        return {"error": f"Failed to fetch Figma file: {response.status_code}"}

    # === GIT INTEGRATION ===
    
    def git_get_repo_status(self, repo_path: str = ".") -> Dict:
        """Get current git status and recent activity"""
        try:
            # Get current status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=repo_path, capture_output=True, text=True
            )
            
            # Get recent commits
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=repo_path, capture_output=True, text=True
            )
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path, capture_output=True, text=True
            )
            
            repo_status = {
                "changed_files": status_result.stdout.strip().split('\n') if status_result.stdout.strip() else [],
                "recent_commits": log_result.stdout.strip().split('\n') if log_result.stdout.strip() else [],
                "current_branch": branch_result.stdout.strip(),
                "has_changes": bool(status_result.stdout.strip())
            }
            
            # Update project context
            repo_name = Path(repo_path).name
            self.update_context(f"git_repo_{repo_name}", repo_status, relevance=8)
            
            return repo_status
            
        except Exception as e:
            return {"error": str(e)}

    def git_track_all_repos(self, base_paths: List[str] = None) -> Dict:
        """Track status of all git repositories"""
        if not base_paths:
            base_paths = [
                str(Path.home() / "REPOS"),
                str(Path.home() / "Projects"),
                str(Path.cwd())
            ]
        
        all_repos = {}
        
        for base_path in base_paths:
            if Path(base_path).exists():
                for item in Path(base_path).iterdir():
                    if item.is_dir() and (item / ".git").exists():
                        repo_status = self.git_get_repo_status(str(item))
                        all_repos[item.name] = repo_status
        
        # Store summary in context
        active_repos = {name: status for name, status in all_repos.items() if status.get('has_changes')}
        self.update_context("active_git_repos", active_repos, relevance=9)
        
        return all_repos

    # === LIFE MANAGEMENT ===
    
    def life_daily_check_in(self) -> None:
        """ADHD-friendly daily check-in with all systems"""
        console.print(Panel.fit(
            "[bold cyan]🌟 Beth's Daily Life Dashboard[/bold cyan]\n"
            "[dim]Your unified command center[/dim]",
            border_style="cyan"
        ))
        
        # Get recent context
        recent_context = self.get_relevant_context("daily check-in")
        
        # Notion status
        notion_summary = self._get_notion_daily_summary()
        
        # Git status
        git_summary = self.git_track_all_repos()
        active_repos = {k: v for k, v in git_summary.items() if v.get('has_changes')}
        
        # Create panels
        panels = []
        
        # Tasks panel
        if notion_summary.get('urgent_tasks'):
            tasks_content = "\n".join([f"• {task}" for task in notion_summary['urgent_tasks'][:3]])
            panels.append(Panel(tasks_content, title="🎯 Today's Focus", border_style="green"))
        
        # Git activity panel
        if active_repos:
            git_content = "\n".join([f"• {repo}: {len(status.get('changed_files', []))} changes" 
                                   for repo, status in list(active_repos.items())[:3]])
            panels.append(Panel(git_content, title="🔧 Active Code", border_style="blue"))
        
        # Memory panel
        if recent_context:
            console.print(f"\n[dim]💭 Recent context: {recent_context[:100]}...[/dim]")
        
        if panels:
            console.print(Columns(panels))
        else:
            console.print("[dim]All quiet on the digital front! 🌱[/dim]")

    def _get_notion_daily_summary(self) -> Dict:
        """Get today's Notion summary"""
        try:
            # Get today's focus tasks
            today = date.today().isoformat()
            
            # Inbox items needing processing
            inbox_results = self.notion.databases.query(
                database_id=self.databases['tasks'],
                filter={"property": "Status", "status": {"equals": "In Inbox"}},
                page_size=10
            )
            
            # Next Actions ready to work on
            next_actions = self.notion.databases.query(
                database_id=self.databases['tasks'],
                filter={"property": "Status", "status": {"equals": "Do Next"}},
                page_size=5
            )
            
            # Display Inbox (limit to reduce overwhelm)
            if inbox_results['results']:
                console.print(f"\n[yellow]📥 Inbox ({len(inbox_results['results'])} items)[/yellow]")
                for i, task in enumerate(inbox_results['results'][:3]):  # Show only first 3
                    title = task['properties']['Task name']['title'][0]['text']['content']
                    console.print(f"  {i+1}. {title}")
                if len(inbox_results['results']) > 3:
                    console.print(f"  ... and {len(inbox_results['results']) - 3} more")
                console.print(f"[dim]💡 Process these during your 10-minute morning routine[/dim]")
            
            # Display Next Actions (ADHD-friendly limit of 3)
            if next_actions['results']:
                console.print(f"\n[green]🎯 Ready to Work On[/green]")
                for i, task in enumerate(next_actions['results'][:3]):
                    title = task['properties']['Task name']['title'][0]['text']['content']
                    priority = task['properties'].get('Priority', {}).get('select', {}).get('name', 'Medium')
                    console.print(f"  {i+1}. {title} [{priority} priority]")
            else:
                console.print(f"\n[green]🎯 No Next Actions ready[/green]")
                console.print(f"[dim]Process your inbox to identify next actions![/dim]")
            
            # Show recent context as a string
            if recent_context:
                console.print(f"\n[dim]💭 Recent context: {recent_context[:100]}...[/dim]")
            
            return {"urgent_tasks": [task['properties']['Task name']['title'][0]['text']['content'] for task in inbox_results['results'][:3]]}
        except Exception as e:
            console.print(f"[red]Error accessing tasks: {e}[/red]")
            console.print("[dim]Make sure your TASKS_DATABASE_ID is configured correctly[/dim]")
        
        return {}

    def ai_life_advisor(self, query: str) -> str:
        """AI advisor with full context awareness"""
        context = self.get_relevant_context(query)
        
        advisor_prompt = f"""
        You are Beth's personal AI advisor with access to her complete digital life context.
        
        QUERY: {query}
        
        AVAILABLE CONTEXT:
        - Recent conversations: {context['recent_conversations'][:3]}
        - Persistent context: {context['persistent_context']}
        - Current date/time: {datetime.now().isoformat()}
        
        BETH'S SYSTEM DETAILS:
        - Uses PARA method for organization
        - Has ADHD - needs clear, actionable advice
        - Manages business (clients, projects, brand assets)
        - Tracks health (appointments, symptoms)
        - Codes (multiple git repos)
        - Designs (Figma files)
        
        Provide specific, actionable advice that:
        1. References relevant context from her digital tools
        2. Suggests concrete next steps
        3. Considers her ADHD needs (not overwhelming)
        4. Integrates across her tools when helpful
        
        Be conversational but practical.
        """
        
        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": advisor_prompt}],
            max_tokens=500
        )
        
        advice = response.choices[0].message.content
        
        # Remember this interaction
        self.remember_conversation(
            query, advice, 
            context_tags=["life_advice", "ai_advisor"],
            importance=7
        )
        
        return advice

# === CLI COMMANDS ===

@click.group()
def cli():
    """Beth's Unified Personal AI Agent"""
    pass

@cli.command()
@click.argument('text')
def capture(text):
    """Smart capture across all systems"""
    agent = BethUnifiedAgent()
    result = agent.notion_smart_capture(text)
    
    if result.get('success'):
        console.print(f"✅ Captured to {result['analysis'].get('database', 'unknown')} system")
        if result['analysis'].get('suggested_actions'):
            console.print(f"💡 Suggestion: {result['analysis']['suggested_actions']}")
    else:
        console.print(f"❌ Error: {result.get('error')}")

@cli.command()
def daily():
    """Unified daily dashboard"""
    agent = BethUnifiedAgent()
    agent.life_daily_check_in()

@cli.command()
@click.argument('query')
def ask(query):
    """Ask your AI advisor anything"""
    agent = BethUnifiedAgent()
    advice = agent.ai_life_advisor(query)
    
    console.print(Panel(advice, title="🧠 Your AI Advisor", border_style="cyan"))

@cli.command()
def git_status():
    """Check all git repositories"""
    agent = BethUnifiedAgent()
    repos = agent.git_track_all_repos()
    
    table = Table(title="🔧 Git Repository Status")
    table.add_column("Repository", style="cyan")
    table.add_column("Branch", style="green")
    table.add_column("Changes", style="yellow")
    
    for repo_name, status in repos.items():
        if 'error' not in status:
            changes = len(status.get('changed_files', []))
            table.add_row(
                repo_name,
                status.get('current_branch', 'unknown'),
                str(changes) if changes > 0 else "clean"
            )
    
    console.print(table)

@cli.command()
@click.argument('file_key')
@click.option('--project', help='Project name for tracking')
def figma_track(file_key, project):
    """Track Figma file changes"""
    agent = BethUnifiedAgent()
    result = agent.figma_track_design_changes(file_key, project)
    
    if result.get('success'):
        console.print(f"✅ Tracking Figma file: {result['file_data'].get('name')}")
    else:
        console.print(f"❌ Error: {result.get('error')}")

@cli.command()
def memory():
    """View recent conversation memory"""
    agent = BethUnifiedAgent()
    context = agent.get_relevant_context("memory review")
    
    console.print(Panel.fit("🧠 Recent Memory", border_style="purple"))
    
    for convo in context['recent_conversations'][:5]:
        timestamp = datetime.fromisoformat(convo[3]).strftime("%m/%d %H:%M")
        console.print(f"[dim]{timestamp}[/dim] {convo[0][:60]}...")

@cli.command()
def setup():
    """Setup unified agent configuration"""
    console.print("🚀 Setting up Beth's Unified AI Agent...")
    
    # Check for required environment variables
    required_vars = [
        "NOTION_TOKEN", "OPENAI_API_KEY",
        "TASKS_DATABASE_ID", "PROJECTS_DATABASE_ID", "NOTES_DATABASE_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        console.print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        console.print("Please check your .env file and beth_setup_guide.md")
    else:
        console.print("✅ All required variables configured!")
        
        # Initialize agent to create memory database
        agent = BethUnifiedAgent()
        console.print("✅ Memory database initialized")
        console.print("✅ Ready to use! Try: python beth_unified_agent.py daily")

if __name__ == "__main__":
    cli() 