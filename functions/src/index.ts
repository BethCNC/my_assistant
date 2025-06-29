/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import * as functions from "firebase-functions/v1";
import * as admin from "firebase-admin";
import fetch from "node-fetch";

// Start writing functions
// https://firebase.google.com/docs/functions/typescript

// For cost control, you can set the maximum number of containers that can be
// running at the same time. This helps mitigate the impact of unexpected
// traffic spikes by instead downgrading performance. This limit is a
// per-function limit. You can override the limit for each function using the
// `maxInstances` option in the function's options, e.g.
// `onRequest({ maxInstances: 5 }, (req, res) => { ... })`.
// NOTE: setGlobalOptions does not apply to functions using the v1 API. V1
// functions should each use functions.runWith({ maxInstances: 10 }) instead.
// In the v1 API, each function can only serve one request per container, so
// this will be the maximum concurrent request count.

admin.initializeApp();
const db = admin.firestore();

// Get OpenAI API key from environment variable
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || functions.config()?.openai?.key;

// Helper: Get chat history for context
async function getChatHistory(chatId: string) {
  const messagesSnap = await db.collection("chats").doc(chatId).collection("messages").orderBy("createdAt", "asc").get();
  return messagesSnap.docs.map((doc) => doc.data() as {sender: string; text: string; createdAt: any});
}

// Helper: (Optional) RAG/Memory logic placeholder
async function getRagContext(chatHistory: Array<{sender: string; text: string; createdAt: any}>) {
  // TODO: Add your retrieval logic here (e.g., search docs, vector db, etc.)
  console.log("Chat history length:", chatHistory.length);
  return "";
}

// Main function: Respond to new user messages (using v1 API)
export const processUserMessage = functions.firestore
  .document("chats/{chatId}/messages/{msgId}")
  .onCreate(async (snap: functions.firestore.QueryDocumentSnapshot, context: functions.EventContext) => {
    try {
      const data = snap.data();
      if (!data) return null;
      if (data.sender !== "user") return null;

      if (!OPENAI_API_KEY) {
        console.error("OpenAI API key not configured");
        return null;
      }

      const chatId = context.params.chatId;

      // Get chat history for context
      const chatHistory = await getChatHistory(chatId);

      // (Optional) Get extra context for RAG
      const ragContext = await getRagContext(chatHistory);

      // Build messages for OpenAI Chat API
      const messages = [
        {
          role: "system",
          content: ragContext ? `Context: ${ragContext}` : "You are a helpful assistant.",
        },
        ...chatHistory.slice(-10).map((m: {sender: string; text: string; createdAt: any}) => ({
          role: m.sender === "user" ? "user" : "assistant",
          content: m.text,
        })),
      ];

      // Call OpenAI Chat Completions API
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages,
          max_tokens: 200,
          temperature: 0.7,
        }),
      });

      const result = await response.json();
      const aiText = result.choices?.[0]?.message?.content?.trim() || "Sorry, I could not generate a response.";

      // Write assistant reply to Firestore
      await db.collection("chats").doc(chatId).collection("messages").add({
        text: aiText,
        sender: "assistant",
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
      });

      return null;
    } catch (error) {
      console.error("Error in processUserMessage:", error);
      return null;
    }
  });
