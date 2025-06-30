# Legacy Code & Data Archive

This folder contains legacy code, scripts, and modules that are **not part of the main workflow** for Beth Assistant, but are preserved for reference and to avoid data/code loss.

## Why Archive?
- To prevent confusion and duplication in the main codebase
- To centralize all chat/memory/context logic on Firestore/Cloud Functions/JS
- To ensure no valuable code or data is lost during refactor

## What Was Moved Here

- `notion_integration_legacy/` (from `medical-data-analysis/src/notion_integration/`)
  - All legacy Notion API integration, mapping, and sync code
- `vectordb_legacy/` (from `medical-data-analysis/src/ai/vectordb/`)
  - All FAISS/vector DB and related memory/context code
- `scripts_legacy/` (from `medical-data-analysis/scripts/`)
  - All legacy scripts, including those using Notion, OpenAI, or custom memory/context logic

## How to Use
- **Do not edit or run code in this folder as part of the main workflow.**
- Reference only if you need to recover logic, data, or ideas from the legacy system.
- All new development should use Firestore/Cloud Functions/JS for chat, memory, and context.

---

If you need to restore or review any legacy logic, check here first before deleting anything permanently.
