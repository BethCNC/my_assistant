# Beth's Unified Personal AI Agent 🧠✨

Your complete digital life assistant that connects Notion, Figma, Git repositories, and remembers everything you discuss. Built with ADHD-friendly design and your PARA method workflow.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup your unified agent
python beth_unified_agent.py setup

# Your daily command center (Notion + Git + Memory + Life)
python beth_unified_agent.py daily

# Smart capture with AI categorization and memory context  
python beth_unified_agent.py capture "Design new client onboarding flow"

# Ask your AI advisor anything - it remembers your conversations
python beth_unified_agent.py ask "What should I focus on today?"

# Track all your git repositories
python beth_unified_agent.py git-status

# Legacy Notion-only commands still available
python notion_agent.py daily                    # Original Notion-focused dashboard
```

## 🌟 What's New: Unified Agent

### **Beyond Notion**: Your Complete Digital Assistant
- **🧠 Memory System**: Remembers all conversations and builds context over time
- **🔧 Git Integration**: Tracks all your repositories and development work  
- **🎨 Figma Tracking**: Monitors design files and connects them to projects
- **💡 AI Life Advisor**: Ask questions about anything - work, life, projects
- **🔗 Cross-Tool Intelligence**: Connects insights across all your tools

## Your Personalized Features

### 🧠 Daily Command Center (ADHD-Optimized)
```bash
python notion_agent.py daily
```
- **Inbox overview** (max 3 items shown to avoid overwhelm)
- **Next Actions** ready to work on (energy-matched)
- **Visual hierarchy** with colors and emojis
- **Cognitive load reduction** - only essential info displayed

### 🚀 Smart Capture (PARA Method)
```bash
python notion_agent.py capture "Research new client onboarding tools"
```
- **AI categorization**: tasks vs notes vs health vs business
- **Automatic routing** to correct database (Tasks/Notes/Health Calendar)
- **Life Area detection**: Personal/Work/Health
- **Energy level assessment**: High/Medium/Low cognitive demand

### 📥 Inbox Processing (10-Minute Sessions)
```bash
python notion_agent.py inbox
```
- **ADHD-friendly timer** - max 10 minutes to avoid burnout
- **AI suggestions** for each item categorization  
- **Two-minute rule** integration
- **Progress tracking** - see how many items you processed

### 💼 Business Dashboard
```bash
python notion_agent.py business
```
- **Active projects** overview
- **Client deadlines** and deliverables
- **Invoice follow-ups** needed
- **Brand asset status** tracking

### 🏥 Health Dashboard  
```bash
python notion_agent.py health
```
- **Upcoming appointments** in next 7 days
- **Medication reminders** 
- **Symptom tracking** quick access
- **Medical team** contact info

### 📊 Weekly Review (Expert-Enhanced)
```bash
python notion_agent.py review
```
- **PARA method analysis** - accomplishments by Life Area
- **AI insights** on productivity patterns
- **Energy management** suggestions
- **Next week focus** recommendations

## Setup for Your System

### 1. API Keys
- **Notion**: https://www.notion.so/my-integrations
- **OpenAI**: https://platform.openai.com/api-keys

### 2. Database IDs
Get these from your database URLs:

```env
TASKS_DATABASE_ID=abc123...          # Your main Tasks database
PROJECTS_DATABASE_ID=def456...       # Your Projects database  
NOTES_DATABASE_ID=ghi789...          # Your Notes database
CLIENTS_DATABASE_ID=jkl012...        # Your Clients database
HEALTH_CALENDAR_DATABASE_ID=mno345...# Your Medical Calendar
```

### 3. Cursor Integration
Update `.vscode/tasks.json` with:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Daily Dashboard",
      "type": "shell",
      "command": "python",
      "args": ["notion_agent.py", "daily"],
      "group": "build"
    },
    {
      "label": "Quick Capture",
      "type": "shell", 
      "command": "python",
      "args": ["notion_agent.py", "capture", "${input:captureText}"],
      "group": "build"
    },
    {
      "label": "Process Inbox",
      "type": "shell",
      "command": "python", 
      "args": ["notion_agent.py", "inbox"],
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

**Quick Access**: `Cmd+Shift+P` → "Tasks: Run Task" → Choose your command

## How It Works with Your System

### PARA Method Integration
- **Projects**: Active work with clear deliverables
- **Areas**: Life domains (Personal/Work/Health) with ongoing maintenance
- **Resources**: Your Notes database with AI-enhanced organization
- **Archive**: Automatic archiving of completed items

### Business Operations Support
- **Client workflow**: Capture → Projects → Tasks → Deliverables
- **Asset management**: Brand assets linked to projects and clients  
- **Financial tracking**: Invoice reminders and payment follow-ups
- **Communication**: Client check-ins and project status updates

### Health Management Integration
- **Appointment prep**: AI-generated preparation tasks
- **Symptom tracking**: Quick capture with date/time stamps
- **Medication management**: Reminder integration with daily workflow
- **Medical team**: Easy access to provider information

### ADHD-Friendly Design Principles
- **Cognitive load reduction**: Limited choices, clear visual hierarchy
- **Energy-task matching**: Match work to your current energy level
- **Progressive disclosure**: Show only relevant information
- **Button automation**: One-click workflows for common actions

## Expert Methodology Integration

### Marie Poulin's ADHD-Conscious Design ✅
- Visual simplification and reduced decision points
- Energy-based task organization
- Button automations for quick actions

### Tiago Forte's PARA Method ✅  
- Action-based organization over subject-based
- Project-first thinking for all captured information
- Just-in-time organization principles

### August Bradley's PPV Framework ✅
- Life Areas aligned with long-term priorities
- Knowledge resurfacing through AI connections
- Focus and alignment between daily actions and life goals

### Thomas Frank's Database Architecture ✅
- Everything connected through relationships
- Formula-driven automation and insights
- Specialized views for different contexts

## Daily Workflows

### Morning Routine (10 minutes)
1. `python notion_agent.py daily` - See your command center
2. `python notion_agent.py inbox` - Process 3-5 inbox items max
3. Choose **3 focus tasks** for the day (ADHD-friendly limit)

### Throughout the Day
- `python notion_agent.py capture "thought"` - Instant capture
- Work from **Next Actions** only - avoid task switching
- Use **energy matching** - high-energy work during peak times

### Evening Routine (5 minutes)  
1. Mark completed tasks as done
2. Quick capture of final thoughts
3. Preview tomorrow's potential focus

### Weekly (30 minutes)
1. `python notion_agent.py review` - PARA method analysis
2. `python notion_agent.py business` - Client and project check
3. `python notion_agent.py health` - Medical appointments and tracking

## Troubleshooting

**Database Connection Issues**: 
- Verify database IDs in `.env` file
- Ensure Notion integration has access to all databases
- Check database property names match your setup

**AI Suggestions Not Working**:
- Verify OpenAI API key is valid
- Check internet connection
- Try simpler capture text to test

**Overwhelming Information**:
- Use the **Emergency Reset Protocol**:
  1. Focus only on `daily` command
  2. Process max 3 tasks per session
  3. Ignore complex features until comfortable

## Advanced Customization

### Custom Property Mapping
Edit `notion_agent.py` to match your exact database properties:

```python
# Update these to match your database schema
"Task": {"title": [{"text": {"content": analysis["title"]}}]},
"Status": {"select": {"name": analysis["category"]}},
"Priority": {"select": {"name": analysis["priority"]}},
```

### Energy-Based Views
Create filtered views in Notion:
- **High Energy Tasks**: Complex creative work, client calls
- **Medium Energy Tasks**: Administrative work, planning
- **Low Energy Tasks**: Filing, organizing, reviewing

### Custom AI Prompts
Modify the AI context in `_load_system_context()` to include your specific:
- Project types and workflows
- Client communication preferences  
- Health tracking priorities
- Personal productivity patterns

---

*Built specifically for your neurodivergent brain, PARA methodology, and integrated life-business-health management. 🧠✨* 