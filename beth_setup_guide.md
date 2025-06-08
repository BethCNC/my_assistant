# 🛠️ Beth's AI Agent Setup Guide

## Quick Setup Checklist

### ✅ Step 1: Install & Configure
```bash
# In your my_assistant directory
pip install -r requirements.txt
python notion_agent.py setup
```

### ✅ Step 2: Update `.env` File

Copy your actual database IDs from Notion URLs:

```env
# API Keys (you already have these)
NOTION_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
FIGMA_ACCESS_TOKEN=your_figma_token_here

# Your Database IDs (get from URL bar when viewing each database)
TASKS_DATABASE_ID=abc123def456...
PROJECTS_DATABASE_ID=abc123def456...
NOTES_DATABASE_ID=abc123def456...
CLIENTS_DATABASE_ID=abc123def456...
HEALTH_CALENDAR_DATABASE_ID=abc123def456...
```

**How to find Database IDs:**
1. Open each database in Notion
2. Copy the long ID from the URL: `notion.so/yourworkspace/DATABASE_ID?v=...`
3. Paste into `.env` file

### ✅ Step 3: Grant Database Access

Your Notion integration needs access to these databases:
1. Go to each database in Notion
2. Click "..." → "Add connections"
3. Select your integration
4. Repeat for all 5 databases

### ✅ Step 4: Test Core Functions

```bash
# Test daily dashboard
python notion_agent.py daily

# Test smart capture  
python notion_agent.py capture "Test AI agent setup"

# Test AI suggestions
python notion_agent.py suggest "organize my client projects"
```

## Your Database Property Mapping

The agent expects these properties in your databases:

### Tasks Database
- **Task** (Title field)
- **Status** (Select: "Inbox", "Next Action", "In Progress", "Waiting For", "Someday Maybe", "Completed")
- **Priority** (Select: "High", "Medium", "Low") 
- **Life Area** (Select: "Personal", "Work", "Health")
- **Energy Level** (Select: "High", "Medium", "Low")
- **Created** (Date field)

### Projects Database  
- **Name** (Title field)
- **Status** (Select with your project statuses)
- **Life Area** (Select: "Personal", "Work", "Health")

### Notes Database
- **Name** (Title field) 
- **Type** (Select with your content types)
- **Life Area** (Select: "Personal", "Work", "Health")
- **Created** (Date field)

### Health Calendar Database
- **Name** (Title field)
- **Date** (Date field)
- **Type** (Select for appointment types)

## Customization for Your Specific Setup

### Property Name Adjustments
If your properties have different names, edit `notion_agent.py`:

```python
# Line ~180 in _create_task method
"properties": {
    "Task": {"title": [{"text": {"content": analysis["title"]}}]},  # Change "Task" to your title field
    "Status": {"select": {"name": analysis["category"]}},           # Change "Status" to your status field
    "Priority": {"select": {"name": analysis["priority"]}},        # etc.
}
```

### Status Options Mapping
Update the status values to match your existing statuses:

```python
# In smart_capture method analysis
"category": "Inbox"|"Next Action"|"Someday Maybe"  # Match your exact status names
```

## Advanced Integrations

### Cursor Tasks Setup
Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0", 
  "tasks": [
    {
      "label": "📊 Daily Dashboard",
      "type": "shell",
      "command": "python",
      "args": ["notion_agent.py", "daily"],
      "group": "build",
      "presentation": {"focus": true}
    },
    {
      "label": "📥 Process Inbox", 
      "type": "shell",
      "command": "python",
      "args": ["notion_agent.py", "inbox"],
      "group": "build"
    },
    {
      "label": "💼 Business Dashboard",
      "type": "shell", 
      "command": "python",
      "args": ["notion_agent.py", "business"],
      "group": "build"
    },
    {
      "label": "🏥 Health Dashboard",
      "type": "shell",
      "command": "python", 
      "args": ["notion_agent.py", "health"],
      "group": "build"
    },
    {
      "label": "🚀 Quick Capture",
      "type": "shell",
      "command": "python",
      "args": ["notion_agent.py", "capture", "${input:captureText}"],
      "group": "build"
    }
  ],
  "inputs": [
    {
      "id": "captureText",
      "description": "What do you want to capture?",
      "type": "promptString"
    }
  ]
}
```

**Quick Access**: `Cmd+Shift+P` → "Tasks: Run Task" → Pick your command

### Alfred/Raycast Integration (Optional)
Create shortcuts for instant access:

```bash
# Alfred workflow or Raycast script
python /Users/bethcartrette/REPOS/my_assistant/notion_agent.py capture "$1"
```

## Troubleshooting Your Setup

### Common Issues

**❌ "Database not found"**
- Double-check database ID in `.env` 
- Ensure integration has access to database
- Database ID should be 32 characters (no hyphens)

**❌ "Property 'Task' not found"** 
- Your title field might have a different name
- Check your database schema and update the code

**❌ "AI suggestions not working"**
- Verify OpenAI API key is valid
- Check internet connection
- Try a simpler capture text first

**❌ "Empty results from daily dashboard"**
- Make sure you have tasks with "Inbox" and "Next Action" statuses
- Check that property names match exactly (case-sensitive)

### Next Steps After Setup

1. **Start with Daily Command Center**: `python notion_agent.py daily`
2. **Capture a few test items**: Try different types (tasks, notes, health, business)
3. **Process your inbox**: `python notion_agent.py inbox` - start with just 2-3 items
4. **Try weekly review**: `python notion_agent.py review` 
5. **Customize**: Adjust status names and properties to match your exact setup

### ADHD-Friendly Usage Tips

- **Start small**: Use only `daily` and `capture` commands first
- **10-minute rule**: Never spend more than 10 minutes processing inbox
- **Energy matching**: Use energy levels to pick appropriate tasks
- **Visual cues**: The colored outputs help reduce cognitive load
- **Emergency reset**: If overwhelmed, just use `python notion_agent.py daily`

---

**🎯 Goal**: Get your AI agent working with your existing PARA system in under 30 minutes, then gradually add advanced features as you get comfortable. 