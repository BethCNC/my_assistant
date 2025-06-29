// Firebase Cloud Function: Responds to new user chat messages with OpenAI, using Firestore v1 API only.
import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import fetch from "node-fetch";
import * as FirebaseFirestore from "firebase-admin/firestore";

admin.initializeApp();
const db = admin.firestore();

// Set your OpenAI API key in functions config: firebase functions:config:set openai.key="sk-..."
const OPENAI_API_KEY = functions.config().openai.key;

// Helper: Get chat history for context
async function getChatHistory(chatId: string) {
  const messagesSnap = await db.collection("chats").doc(chatId).collection("messages").orderBy("createdAt", "asc").get();
  return messagesSnap.docs.map((doc) => doc.data());
}

// Helper: (Optional) RAG/Memory logic placeholder
async function getRagContext(chatHistory: any[]) {
  // TODO: Add your retrieval logic here (e.g., search docs, vector db, etc.)
  return "";
}

// Main function: Respond to new user messages
export const onUserMessage = functions.firestore
  .document("chats/{chatId}/messages/{msgId}")
  .onCreate(async (snap: FirebaseFirestore.DocumentSnapshot, context: functions.EventContext) => {
    const data = snap.data();
    if (!data) return null;
    if (data.sender !== "user") return null;
    const chatId = context.params.chatId;
    // Get chat history for context
    const chatHistory = await getChatHistory(chatId);
    // (Optional) Get extra context for RAG
    const ragContext = await getRagContext(chatHistory);
    // Build prompt for OpenAI
    const historyText = chatHistory.map((m) => `${m.sender === "user" ? "User" : "Assistant"}: ${m.text}`).join("\n");
    const prompt = `${ragContext ? `Context: ${ragContext}\n` : ""}${historyText}\nAssistant:`;
    // Call OpenAI
    const response = await fetch("https://api.openai.com/v1/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "text-davinci-003",
        prompt,
        max_tokens: 200,
        temperature: 0.7,
        stop: ["User:", "Assistant:"],
      }),
    });
    const result = await response.json();
    const aiText = result.choices?.[0]?.text?.trim() || "Sorry, I could not generate a response.";
    // Write assistant reply to Firestore
    await db.collection("chats").doc(chatId).collection("messages").add({
      text: aiText,
      sender: "assistant",
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    return null;
  }); 