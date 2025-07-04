import { useState, useEffect, useCallback } from 'react';
import { db } from '../utils/firebase';
import {
  collection,
  addDoc,
  query,
  orderBy,
  onSnapshot,
  serverTimestamp,
  Timestamp,
  doc,
  setDoc,
  deleteDoc,
  getDocs,
  getDoc
} from 'firebase/firestore';

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  createdAt: Timestamp | null;
}

export interface UseChatOptions {
  chatId?: string;
  autoLoadHistory?: boolean;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => Promise<void>;
  loadHistory: () => Promise<void>;
  chatId?: string;
  setChatId: React.Dispatch<React.SetStateAction<string | undefined>>;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn & {
  memory: any[];
  tasks: any[];
  healthEvents: any[];
  routines: any[];
  personalization: any;
} {
  const { chatId: initialChatId, autoLoadHistory = true } = options;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatId, setChatId] = useState<string | undefined>(initialChatId || 'default');
  const [memory, setMemory] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [healthEvents, setHealthEvents] = useState<any[]>([]);
  const [routines, setRoutines] = useState<any[]>([]);
  const [personalization, setPersonalization] = useState<any>(null);
  const userId = 'default';

  // Real-time Firestore listener
  useEffect(() => {
    if (!chatId) return;
    const q = query(
      collection(db, 'chats', chatId, 'messages'),
      orderBy('createdAt', 'asc')
    );
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const newMessages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })) as ChatMessage[];
      setMessages(newMessages);
    }, (err) => setError(err.message));
    return () => unsubscribe();
  }, [chatId]);

  const loadHistory = useCallback(async () => {
    // No-op: real-time listener handles this
    setError(null);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      await addDoc(collection(db, 'chats', chatId || 'default', 'messages'), {
        text: content.trim(),
        sender: 'user',
        createdAt: serverTimestamp()
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  }, [chatId]);

  const clearMessages = useCallback(async () => {
    if (!chatId) return;
    setIsLoading(true);
    setError(null);
    try {
      // Delete all messages in the chat
      const q = query(collection(db, 'chats', chatId, 'messages'));
      const snapshot = await getDocs(q);
      for (const docSnap of snapshot.docs) {
        await deleteDoc(docSnap.ref);
      }
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear messages');
    } finally {
      setIsLoading(false);
    }
  }, [chatId]);

  useEffect(() => {
    if (autoLoadHistory) loadHistory();
  }, [autoLoadHistory, loadHistory]);

  // Fetch context from Firestore
  const fetchContext = useCallback(async () => {
    try {
      // Memory
      const memQ = query(collection(db, `users/${userId}/memory`), orderBy('createdAt', 'desc'));
      const memSnap = await getDocs(memQ);
      setMemory(memSnap.docs.slice(0, 5).map(doc => ({ id: doc.id, ...doc.data() })));
      // Tasks
      const taskQ = query(collection(db, `users/${userId}/tasks`), orderBy('createdAt', 'desc'));
      const taskSnap = await getDocs(taskQ);
      setTasks(taskSnap.docs.slice(0, 5).map(doc => ({ id: doc.id, ...doc.data() })));
      // Health Events
      const healthQ = query(collection(db, `users/${userId}/healthEvents`), orderBy('date', 'asc'));
      const healthSnap = await getDocs(healthQ);
      setHealthEvents(healthSnap.docs.slice(0, 3).map(doc => ({ id: doc.id, ...doc.data() })));
      // Routines
      const routineQ = query(collection(db, `users/${userId}/routines`), orderBy('createdAt', 'desc'));
      const routineSnap = await getDocs(routineQ);
      setRoutines(routineSnap.docs.slice(0, 3).map(doc => ({ id: doc.id, ...doc.data() })));
      // Personalization
      const persRef = doc(db, `users/${userId}/personalization/main`);
      const persSnap = await getDoc(persRef);
      setPersonalization(persSnap.exists() ? persSnap.data() : null);
    } catch (err) {
      // Silent fail for context
    }
  }, [userId]);

  // Fetch context on mount and after sending a message
  useEffect(() => { fetchContext(); }, [fetchContext]);
  const sendMessageWithContext = useCallback(async (content: string) => {
    await sendMessage(content);
    // Placeholder: send context to backend for RAG/AI
    // Example: call a Cloud Function or REST endpoint with {content, memory, tasks, healthEvents, routines, personalization}
    // await fetch('/api/assistant', { method: 'POST', body: JSON.stringify({ content, memory, tasks, healthEvents, routines, personalization }) })
    await fetchContext();
  }, [sendMessage, fetchContext, memory, tasks, healthEvents, routines, personalization]);

  return {
    messages,
    isLoading,
    error,
    sendMessage: sendMessageWithContext,
    clearMessages,
    loadHistory,
    chatId,
    setChatId,
    memory,
    tasks,
    healthEvents,
    routines,
    personalization
  };
} 