# Firestore Schema: Beth Assistant

This document defines the unified Firestore schema for all assistant data. All chat, memory, context, and personalization logic should use these collections and fields.

---

## chats/{chatId}/messages/{msgId}
```jsonc
{
  "text": string,            // Message content
  "sender": "user" | "assistant",
  "createdAt": timestamp,    // Firestore server timestamp
  "contextTags": [string],   // (optional) For RAG/context
  "energyLevel": string      // (optional) For personalization
}
```

---

## users/{userId}/memory/{memoryId}
```jsonc
{
  "type": "note" | "insight" | "reminder" | "pattern",
  "content": string,         // Memory/note content
  "createdAt": timestamp,
  "relevanceScore": number,  // (optional) For RAG ranking
  "tags": [string]           // (optional) For search/context
}
```

---

## users/{userId}/tasks/{taskId}
```jsonc
{
  "title": string,
  "status": "inbox" | "next" | "someday" | "done",
  "dueDate": timestamp,      // (optional)
  "energy": string,          // (optional) For personalization
  "routineId": string        // (optional) Link to routine
}
```

---

## users/{userId}/healthEvents/{eventId}
```jsonc
{
  "type": "appointment" | "symptom" | "medication" | ...,
  "description": string,
  "date": timestamp,
  "relatedTasks": [string]   // (optional) Task IDs
}
```

---

## users/{userId}/routines/{routineId}
```jsonc
{
  "name": string,
  "steps": [string],
  "frequency": string,       // e.g. "daily", "weekly"
  "lastCompleted": timestamp
}
```

---

## users/{userId}/personalization/main
```jsonc
{
  "energyProfile": object,   // e.g. {morning: "low", afternoon: "high"}
  "routineAdherence": object,
  "focusTimes": [string],
  "preferences": object      // Arbitrary user preferences
}
```

---

> All new features and data should extend this schema. Update this file with any changes to keep the team in sync. 