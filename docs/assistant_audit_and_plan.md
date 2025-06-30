# Assistant System Audit & Refactor Plan

## 1. Legacy/Non-Firebase Logic Detected

### Python CLI Agents
- `tools/beth_unified_agent.py`:
  - Uses **SQLite** for conversation memory/context
  - Integrates with **Notion**, **Figma**, **Git**, and **OpenAI** directly
  - Handles smart capture, life dashboard, and AI advisor logic
- `tools/notion_agent.py`:
  - Uses **Notion API** for all data (tasks, projects, notes, health, clients)
  - Uses **OpenAI** for suggestions, context, and smart capture
  - No Firestore/Firebase integration

### Medical Data Pipeline
- `medical-data-analysis/` and submodules:
  - RAG, vector DB, and entity extraction logic in Python
  - No Firestore integration; uses local files and possibly SQLite/FAISS

### Frontend/Cloud Functions
- `functions/src/index.ts` and `src/index.ts`:
  - Firestore is used for chat storage
  - RAG/context logic is a placeholder (TODO)
  - Calls OpenAI API directly for completions
  - No persistent, structured memory or learning from user patterns

### Chat UI
- `frontend/components/FunctionalChatInterface.tsx`:
  - Loads conversations from API client (may still reference old endpoints)
  - Contextual suggestions logic is present, but not deeply integrated with Firestore or learning

## 2. What Needs to Be Removed or Replaced
- **All SQLite, FastAPI, and direct Notion integrations** for chat/memory/context
- **Direct OpenAI calls** that bypass Firestore for context/history
- **Python-based memory and RAG logic** (unless ported to Firestore/JS)
- **Legacy backend endpoints and configs**

## 3. What Needs to Be Refactored or Added
- **Firestore as the single source of truth** for all chat, memory, context, and learning
- **RAG pipeline** that retrieves relevant context from Firestore (chat history, notes, tasks, health, etc.)
- **Personalization layer** that adapts to ADHD/autism needs (energy, routines, reminders, context prompts)
- **Smart suggestions and routines** based on user patterns, stored in Firestore
- **Unified dashboard and daily insights** powered by Firestore data
- **Remove all legacy code and configs** that could cause confusion

## 4. Other Relevant Findings
- Medical data and life context are scattered across Notion, local files, and Python scripts—need to unify into Firestore
- Design system and UI logic are mostly up-to-date, but context-awareness and learning are not yet implemented
- Offline mode and fallback logic are present, but not deeply integrated with learning/memory

---

## 🔨 Full Refactor & Feature Plan: Making Beth's Assistant Truly Personal

### **Phase 1: Remove Legacy Code & Centralize on Firestore**
- [ ] Delete all SQLite, FastAPI, and direct Notion/OpenAI integrations for chat/memory/context
- [ ] Remove Python-based memory and RAG logic (unless ported to Firestore/JS)
- [ ] Ensure all chat, memory, and context data is stored and retrieved from Firestore only
- [ ] Update frontend to use Firestore for all chat history and suggestions
- [ ] Clean up configs, scripts, and endpoints to avoid confusion

### **Phase 2: Firestore-Based RAG Pipeline**
- [ ] Design Firestore schema for storing all relevant data: chat history, notes, tasks, health events, routines, etc.
- [ ] Implement a retrieval layer (in Cloud Functions or frontend) to fetch relevant context for each chat message
- [ ] Integrate this context into the prompt for OpenAI completions (via Cloud Functions)
- [ ] Ensure the assistant can reference and cite real history, notes, and events in its answers
- [ ] Add support for searching and summarizing across all Firestore data

### **Phase 3: Learning & Personalization (ADHD/Autism Support)**
- [ ] Track user patterns: energy levels, routines, preferred workflows, common struggles
- [ ] Store and update personalization data in Firestore (e.g., "energy profile", "routine adherence", "focus times")
- [ ] Use this data to:
    - Adapt suggestions and reminders to user's energy and executive function
    - Offer context prompts and nudges based on past behavior
    - Surface routines and checklists at the right time
- [ ] Build a feedback loop: let user rate/help tune suggestions and routines

### **Phase 4: Dashboard, Daily Insights, and Smart Suggestions**
- [ ] Create a daily dashboard UI that pulls from Firestore: tasks, events, health, reminders, insights
- [ ] Implement smart suggestions based on recent activity, context, and learning data
- [ ] Add routines/templates for common workflows (appointment prep, symptom tracking, project review, etc.)
- [ ] Ensure all dashboard and suggestion logic is ADHD/autism-friendly (minimal friction, clear, actionable)

### **Phase 5: Polish, Test, and Document**
- [ ] Test all features for reliability, accessibility, and performance
- [ ] Document new architecture, data flows, and usage patterns in `docs/`
- [ ] Remove any remaining legacy or unused code
- [ ] Gather user feedback and iterate

---

## ✅ **Refactor & Feature Plan Checklist**

- [ ] Legacy code removed (SQLite, FastAPI, Notion, Python RAG)
- [ ] Firestore is the single source of truth for all assistant data
- [ ] RAG pipeline retrieves and injects real context into chat
- [ ] Personalization and learning logic adapts to ADHD/autism needs
- [ ] Dashboard and daily insights are live and actionable
- [ ] Smart suggestions and routines are context-aware
- [ ] All code and docs are up to date and easy to maintain

## Next: Full Refactor & Feature Plan (to be written after audit review)

---

## 🚀 Phase 2: Firestore-Based RAG Pipeline — Design & Implementation Plan

### **Proposed Firestore Schema**

- **chats/{chatId}/messages/{msgId}**
  - `text`: string (message content)
  - `sender`: 'user' | 'assistant'
  - `createdAt`: timestamp
  - `contextTags`: [string] (optional, for RAG)
  - `energyLevel`: string (optional, for personalization)

- **users/{userId}/memory/{memoryId}**
  - `type`: 'note' | 'insight' | 'reminder' | 'pattern'
  - `content`: string
  - `createdAt`: timestamp
  - `relevanceScore`: number
  - `tags`: [string]

- **users/{userId}/tasks/{taskId}**
  - `title`: string
  - `status`: 'inbox' | 'next' | 'someday' | 'done'
  - `dueDate`: timestamp
  - `energy`: string
  - `routineId`: string (optional)

- **users/{userId}/healthEvents/{eventId}**
  - `type`: 'appointment' | 'symptom' | 'medication' | ...
  - `description`: string
  - `date`: timestamp
  - `relatedTasks`: [taskId]

- **users/{userId}/routines/{routineId}**
  - `name`: string
  - `steps`: [string]
  - `frequency`: string (daily, weekly, etc.)
  - `lastCompleted`: timestamp

- **users/{userId}/personalization**
  - `energyProfile`: object (e.g., {morning: 'low', afternoon: 'high'})
  - `routineAdherence`: object
  - `focusTimes`: [string]
  - `preferences`: object

### **Retrieval/Query Strategy for RAG**

1. **On new user message:**
   - Fetch last N (e.g., 10) chat messages for context
   - Query `memory` for recent/high-relevance notes, insights, reminders
   - Query `tasks` for urgent/active tasks
   - Query `healthEvents` for recent/upcoming events
   - Query `routines` for due/active routines
   - Pull personalization data (energy, focus, preferences)

2. **Context Assembly:**
   - Build a context object with:
     - Recent chat
     - Relevant memory/notes
     - Active tasks
     - Health events
     - Routine status
     - Personalization profile

3. **Prompt Construction:**
   - Inject this context into the system prompt for OpenAI (in Cloud Functions)
   - Example:
     ```
     SYSTEM: You are Beth's personal assistant. Here is her current context:
     - Recent chat: ...
     - Memory/notes: ...
     - Tasks: ...
     - Health: ...
     - Routines: ...
     - Energy/focus: ...
     Respond in a way that is ADHD/autism-friendly: clear, actionable, not overwhelming.
     ```

4. **Search & Summarization:**
   - Implement endpoints/functions to search across all user data (chat, memory, tasks, health, routines)
   - Summarize results for queries like "What did I do last week?" or "Summarize my health events this month."

### **ADHD/Autism-Friendly Considerations**
- Always surface context in a clear, non-overwhelming way
- Prioritize actionable next steps and gentle reminders
- Adapt suggestions to user's energy and focus profile
- Use routines/checklists for recurring needs
- Allow user to rate/tune suggestions for better personalization

### **Actionable Steps for Implementation**
1. Finalize Firestore schema and migrate any existing data
2. Update frontend to write/read all assistant data from Firestore
3. Implement context retrieval logic in Cloud Functions
4. Refactor OpenAI prompt construction to use assembled context
5. Add search/summarization endpoints for user queries
6. Test with real user flows and iterate for clarity and usability 