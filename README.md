# Notion AI Assistant 🤖

Your personal AI agent for Notion workspace organization and productivity.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup (interactive)
python notion_agent.py setup

# Start using
python notion_agent.py capture "Build Notion AI agent"
python notion_agent.py search "project ideas"
python notion_agent.py review
```

## Features

### 🚀 Quick Capture
Instantly save ideas/tasks with AI categorization:
```bash
python notion_agent.py capture "Research AI automation tools"
# → Auto-categorizes as "task", sets priority, creates in Notion
```

### 🔍 Smart Search  
AI-enhanced search with suggestions:
```bash
python notion_agent.py search "machine learning"
# → Searches Notion + suggests better terms if no results
```

### 💡 AI Suggestions
Get productivity advice for any task:
```bash
python notion_agent.py suggest "organize my project notes" --context "I have 50+ scattered pages"
```

### 📊 Weekly Review
Automated productivity analysis:
```bash
python notion_agent.py review
# → AI analyzes your week's activity, suggests improvements
```

## Setup

### 1. Get API Keys
- **Notion**: https://www.notion.so/my-integrations
- **OpenAI**: https://platform.openai.com/api-keys

### 2. Configure
Copy `config.env.example` to `.env` and add your keys:
```env
NOTION_TOKEN=secret_...
OPENAI_API_KEY=sk-...
DEFAULT_DATABASE_ID=your-main-database-id
```

### 3. Cursor Integration
Add these to your Cursor workspace settings:

```json
{
  "tasks": {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Capture Idea",
        "type": "shell",
        "command": "python",
        "args": ["notion_agent.py", "capture", "${input:ideaText}"],
        "group": "build"
      },
      {
        "label": "Weekly Review",
        "type": "shell", 
        "command": "python",
        "args": ["notion_agent.py", "review"],
        "group": "build"
      }
    ],
    "inputs": [
      {
        "id": "ideaText",
        "description": "What idea do you want to capture?",
        "default": "",
        "type": "promptString"
      }
    ]
  }
}
```

Then use `Cmd+Shift+P` → "Tasks: Run Task" → "Capture Idea"

## Advanced Usage

### Custom Workflows
Create your own commands by extending the `NotionAgent` class:

```python
def project_standup(self):
    """Generate daily project standup"""
    # Your logic here
    pass
```

### Automation Ideas
- **Daily planning**: Auto-create today's agenda
- **Email processing**: Parse emails → Notion tasks  
- **Meeting notes**: Auto-structure from transcripts
- **Goal tracking**: Weekly progress on objectives

## Troubleshooting

**"Database not found"**: Make sure your Notion integration has access to the database and the ID is correct.

**"API rate limit"**: The script includes basic rate limiting, but heavy usage might need delays.

**Property errors**: The script assumes standard database properties (Name, Category, Priority, Created). Adjust for your schema.

## Next Steps

1. **Try the basic commands** to get familiar
2. **Set up Cursor tasks** for quick access
3. **Customize properties** in `notion_agent.py` to match your databases
4. **Add new commands** for your specific workflows

---

*Built for productivity nerds who want AI assistance without leaving their tools.* 