import { useState, useEffect, useCallback } from 'react';
import { apiClient, ChatMessage } from '@/lib/api';

export interface UseChatOptions {
  conversationId?: string;
  autoLoadHistory?: boolean;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  loadHistory: () => Promise<void>;
  conversationId?: string;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { conversationId, autoLoadHistory = true } = options;
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(conversationId);

  const loadHistory = useCallback(async () => {
    try {
      setError(null);
      const response = await apiClient.getChatHistory(currentConversationId);
      
      if (response.error) {
        setError(response.error);
        return;
      }
      
      if (response.data) {
        // Handle different response formats
        if (currentConversationId) {
          // Single chat response
          const chatData = response.data;
          if (chatData.messages) {
            const formattedMessages = chatData.messages.map((msg: any) => ({
              id: msg.id,
              content: msg.message,
              role: msg.type === 'user' ? 'user' : 'assistant',
              timestamp: msg.timestamp,
              conversation_id: chatData.id,
            }));
            setMessages(formattedMessages);
          }
        } else {
          // All chats response - just show empty for now
          setMessages([]);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load chat history');
    }
  }, [currentConversationId]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately for optimistic UI
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      content: content.trim(),
      role: 'user',
      timestamp: new Date().toISOString(),
      conversation_id: currentConversationId,
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await apiClient.sendMessage(content.trim(), currentConversationId);
      
      if (response.error) {
        setError(response.error);
        // Remove the optimistic message on error
        setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
        return;
      }

      if (response.data) {
        // Backend returns the assistant's response
        let responseContent = 'No response';
        
        if (response.data.reply) {
          // Try to parse the reply if it's a JSON string
          try {
            const parsed = JSON.parse(response.data.reply);
            responseContent = parsed.answer || parsed.response || response.data.reply;
          } catch {
            responseContent = response.data.reply;
          }
        } else if (response.data.response) {
          responseContent = response.data.response;
        } else if (response.data.message) {
          responseContent = response.data.message;
        }

        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          content: responseContent,
          role: 'assistant',
          timestamp: new Date().toISOString(),
          conversation_id: response.data.chat_id || currentConversationId,
        };

        // Update conversation ID if this is a new conversation
        if (response.data.chat_id && !currentConversationId) {
          setCurrentConversationId(response.data.chat_id);
        }

        // Replace temp message and add assistant response
        setMessages(prev => {
          const filtered = prev.filter(msg => msg.id !== userMessage.id);
          return [...filtered, 
            { ...userMessage, id: `user-${Date.now()}` },
            assistantMessage
          ];
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      // Remove the optimistic message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  }, [currentConversationId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setCurrentConversationId(undefined);
  }, []);

  // Load history on mount if enabled
  useEffect(() => {
    if (autoLoadHistory) {
      loadHistory();
    }
  }, [autoLoadHistory, loadHistory]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    loadHistory,
    conversationId: currentConversationId,
  };
} 