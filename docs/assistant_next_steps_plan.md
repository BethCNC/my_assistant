# Beth Assistant: Next Steps & Unified Roadmap

## 🟢 What's Solid / Already Built

- **Frontend:** Next.js app, Figma-accurate UI, chat interface, context suggestions, Firestore integration for chat.
- **Backend:** Google Cloud Functions (Node.js/TypeScript), Firestore for chat/memory, OpenAI API calls, basic RAG logic placeholder.
- **Medical Data Pipeline:** Python pipeline for ingesting, extracting, and analyzing medical data (PDF, CSV, HTML, etc.), vector DB, entity extraction, Notion integration.
- **Multi-tool Integration:** Notion, Figma, Git, Gmail, Google Calendar (some via legacy Python, some via new stack).
- **Design System:** Figma tokens, strict design system, no made-up CSS.
- **Docs:** Extensive documentation, design system, audit/refactor plans, project evolution summaries.

---

## 🔴 What's Missing / Needs Work

### 1. Legacy Code Removal & Centralization
- [x] Remove all SQLite, FastAPI, and direct Notion/OpenAI integrations for chat/memory/context (Python agents, old endpoints).
  - _Done: All legacy/duplicate code archived and main workflow is Firestore/JS only._

### 2. RAG Pipeline (Retrieval-Augmented Generation)
- [x] Implement Firestore-based RAG: retrieve relevant context (chat, notes, tasks, health, routines) for each message.
  - _Done: Backend Cloud Function injects Firestore context into OpenAI prompt._
- [x] Integrate context into OpenAI prompt construction (backend).
  - _Done: System prompt includes all context fields, ADHD/autism-friendly._
- [x] Add endpoints/functions to search and summarize across all Firestore data.
  - _Done: Context retrieval and prompt construction unified in backend._

### 3. Personalization & Learning
- [ ] Track user patterns (energy, routines, focus, struggles) and store in Firestore.
- [ ] Use this data to adapt suggestions, reminders, and context prompts.
- [ ] Build feedback loop for user to rate/tune suggestions.

### 4. Unified Dashboard & Daily Insights
- [ ] Build dashboard UI: tasks, events, health, reminders, insights—all from Firestore.
- [ ] Implement smart, context-aware suggestions and routines.
- [ ] Add routines/templates for common workflows (appointment prep, symptom tracking, etc.).

### 5. Medical Data Pipeline Integration
- [x] Unify medical data pipeline output with Firestore (not just local files/Notion).
  - _Done: Pipeline uploads extracted health events to Firestore automatically._
- [ ] Enable frontend to query and display medical timeline, symptom tracking, provider directory, etc.
- [ ] Automate summary/handout generation for appointments.

### 6. Calendar & Email Consolidation
- [ ] Finish Google Calendar API integration (bi-directional sync with Notion, partner visibility, ADHD-friendly workflows).
- [ ] Integrate Gmail for reading, summarizing, drafting, and organizing messages.

### 7. Testing, Security, and Docs
- [ ] Add/expand unit and integration tests (especially for new Firestore/RAG logic).
- [ ] Ensure HIPAA-compliant data security for medical info.
- [ ] Update docs to reflect new architecture and workflows.

---

## 📝 Next Steps (Actionable Checklist)

1. **[x] Remove legacy Python/SQLite/Notion/OpenAI code for chat/memory/context.**
2. **[x] Finalize Firestore schema for all assistant data (chat, memory, tasks, health, routines, personalization).**
3. **[x] Implement Firestore-based RAG retrieval and context injection in backend.**
4. **[x] Update frontend to use Firestore for all chat, memory, and suggestions.**
5. **[x] Integrate medical data pipeline output with Firestore and frontend UI.**
6. **[ ] Build unified dashboard and daily insights UI.**
7. **[ ] Finish Google Calendar and Gmail integrations (with ADHD-friendly features).**
8. **[ ] Add learning/personalization logic and feedback loop.**
9. **[ ] Expand tests, security, and documentation.**

---

## ⚡️ Prioritization

- **Phase 1:** Remove legacy code, centralize on Firestore, finalize schema. ✅
- **Phase 2:** RAG pipeline, context-aware chat, Firestore integration everywhere. ✅
- **Phase 3:** Personalization, dashboard, medical data integration. ⏳
- **Phase 4:** Calendar/email consolidation, routines/templates, partner sharing. ⏳
- **Phase 5:** Testing, security, docs, polish. ⏳

---

Let this file serve as the working roadmap for Beth Assistant. Check off items as you complete them and update as priorities shift. 