'use client';

import React, { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { useChat } from '@/hooks/use-chat';
import { db } from '../utils/firebase';
import {
  collection,
  getDocs,
  orderBy,
  query as firestoreQuery
} from 'firebase/firestore';
import { SuggestionCard } from './figma-system/SuggestionCard';
import { SuggestionShapeVariant } from './figma-system/SuggestionShapes';
import styles from './ChatInterface.module.css';
import ChatInput from './figma-system/ChatInput';

const FunctionalChatInterface = () => {
  const { messages, isLoading, error, sendMessage, clearMessages, chatId, setChatId, memory, tasks, healthEvents, routines, personalization } = useChat();
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [conversations, setConversations] = useState<any[]>([]);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Function to format chat title for display - moved before usage
  const formatChatTitle = (chat: any) => {
    if (chat.title && chat.title !== 'undefined') {
      return chat.title.length > 30 ? chat.title.substring(0, 30) + '...' : chat.title;
    }
    if (chat.preview) {
      return chat.preview.length > 30 ? chat.preview.substring(0, 30) + '...' : chat.preview;
    }
    return 'Untitled Chat';
  };

  // Context-aware suggestions
  const getContextualSuggestions = () => {
    const suggestions: string[] = [];
    // Urgent tasks
    if (tasks && tasks.length > 0) {
      tasks.slice(0, 2).forEach(t => {
        suggestions.push(`Help me complete: ${t.title || t.text || 'a task'}`);
      });
    }
    // Upcoming health events
    if (healthEvents && healthEvents.length > 0) {
      healthEvents.slice(0, 2).forEach(e => {
        suggestions.push(`Remind me about: ${e.title || e.text || 'an event'}`);
      });
    }
    // Memory notes mentioning energy/focus
    if (memory && memory.length > 0) {
      memory.forEach(m => {
        if ((m.text || '').toLowerCase().includes('energy') || (m.text || '').toLowerCase().includes('focus')) {
          suggestions.push('Summarize my recent energy and focus');
        }
      });
    }
    // Routines
    if (routines && routines.length > 0) {
      routines.slice(0, 1).forEach(r => {
        suggestions.push(`Help me stick to my routine: ${r.title || r.text || 'a routine'}`);
      });
    }
    // Personalization
    if (personalization && personalization.energyLevel) {
      suggestions.push(`Give me advice for my current energy: ${personalization.energyLevel}`);
    }
    // Fallback
    if (suggestions.length === 0) {
      suggestions.push(
        'Tell me about design tokens and system components',
        'Show me information about organizing projects',
        'Can you explain recent GitHub activity',
        'Can you explain calendar events and meetings',
        'I need assistance with creating new tasks',
        'Can you explain searching and managing files'
      );
    }
    return suggestions.slice(0, 6);
  };

  const [suggestions, setSuggestions] = useState(getContextualSuggestions());

  // Use fixed shapes to prevent hydration mismatch (server vs client random differences)
  const suggestionShapes: SuggestionShapeVariant[] = [3, 1, 2, 7, 4, 6];

  // Fetch conversations from Firestore
  useEffect(() => {
    const fetchConversations = async () => {
      const q = firestoreQuery(collection(db, 'chats'));
      const snapshot = await getDocs(q);
      const chats = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setConversations(chats);
    };
    fetchConversations();
  }, []);

  // Update suggestions when conversations change
  useEffect(() => {
    setSuggestions(getContextualSuggestions());
  }, [memory, tasks, healthEvents, routines, personalization]);

  // Function to load a specific chat (switch chatId)
  const handleChatClick = async (newChatId: string) => {
    setShowSuggestions(false);
    if (newChatId !== chatId) setChatId(newChatId);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    setShowSuggestions(false);
    await sendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleSuggestionClick = async (suggestion: string) => {
    setShowSuggestions(false);
    await sendMessage(suggestion);
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const [timeDisplay, setTimeDisplay] = useState({ weekday: '', date: '', time: '' });

  useEffect(() => {
    const formatTime = () => {
      const now = new Date();
      const formatted = now.toLocaleString('en-US', {
        weekday: 'long',
        month: 'long', 
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      }).split(', ');
      
      return {
        weekday: formatted[0],
        date: formatted[1],
        time: formatted[2]
      };
    };

    setTimeDisplay(formatTime());
  }, []);

  return (
    <div style={{width: '100vw', minHeight: '100vh', background: '#f7f7f7', display: 'flex', justifyContent: 'center', alignItems: 'flex-start'}}>
      <div style={{maxWidth: 1200, width: '100%', padding: '48px', boxSizing: 'border-box', display: 'flex', gap: 24}}>
        {/* Sidebar */}
        <div style={{minWidth: 240, maxWidth: 320, background: '#222', borderRadius: 12, padding: 24, color: '#fff', display: 'flex', flexDirection: 'column', gap: 24}}>
          {/* Recents, New Chat, etc. */}
          <div className={styles.recentChats}>
            <div className={styles.labelText}>
              <div className={styles.newChatButton}>Recents</div>
            </div>
            <div className={styles.leadIcon} onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}>
              <Image 
                className={`${styles.arrowIcon} ${isSidebarCollapsed ? styles.arrowCollapsed : ''}`}
                width={24} 
                height={24} 
                alt="Arrow" 
                src="/assets/icons/arrow.svg" 
              />
            </div>
          </div>
          
          {!isSidebarCollapsed && (
            <>
              <div className={styles.leftColumn}>
                <div className={styles.recentChats1}>
                  {conversations.length > 0 ? (
                    conversations.slice(0, 9).map((conv) => (
                      <div 
                        key={conv.id}
                        className={
                          conv.id === chatId
                            ? `${styles.recentChatItem} ${styles.activeChat}`
                            : styles.recentChatItem
                        }
                        onClick={() => handleChatClick(conv.id)}
                      >
                        {formatChatTitle(conv)}
                      </div>
                    ))
                  ) : (
                    // Show placeholder chat history items that match Figma design
                    [
                      'How can I better update my design tokens',
                      'How can I better organize my projects', 
                      'How can I better manage my calendar',
                      'How can I better track my tasks',
                      'How can I better use GitHub workflows',
                      'How can I better structure my files',
                      'How can I better automate my work',
                      'How can I better sync my tools',
                      'How can I better plan my schedule'
                    ].map((placeholderText, i) => (
                      <div key={i} className={styles.chatHistory}>
                        <div className={styles.chatHistory1}>
                          <div className={styles.howCanI}>{placeholderText}</div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                {/* Context Panel */}
                <div style={{marginTop: 24, padding: 16, background: '#f8f9fa', borderRadius: 8, fontSize: 14}}>
                  <div><b>Memory:</b></div>
                  {memory.length === 0 ? <div style={{color:'#aaa'}}>No memory notes</div> : memory.map(m => <div key={m.id}>{m.text || m.content || JSON.stringify(m)}</div>)}
                  <div style={{marginTop: 12}}><b>Tasks:</b></div>
                  {tasks.length === 0 ? <div style={{color:'#aaa'}}>No tasks</div> : tasks.map(t => <div key={t.id}>{t.title || t.text || JSON.stringify(t)}</div>)}
                  <div style={{marginTop: 12}}><b>Health Events:</b></div>
                  {healthEvents.length === 0 ? <div style={{color:'#aaa'}}>No health events</div> : healthEvents.map(e => <div key={e.id}>{e.title || e.text || JSON.stringify(e)}</div>)}
                  <div style={{marginTop: 12}}><b>Routines:</b></div>
                  {routines.length === 0 ? <div style={{color:'#aaa'}}>No routines</div> : routines.map(r => <div key={r.id}>{r.title || r.text || JSON.stringify(r)}</div>)}
                  {personalization && (
                    <div style={{marginTop: 12}}><b>Personalization:</b> {JSON.stringify(personalization)}</div>
                  )}
                </div>
              </div>

              <div className={styles.newChatButton1} onClick={() => {
                clearMessages();
                setShowSuggestions(true);
                // Refresh suggestions and shapes for new chat
                setSuggestions(getContextualSuggestions());
              }}>
                <div className={styles.labelText}>
                  <b className={styles.newChatButton2}>New Chat</b>
                </div>
                <div className={styles.icons}>
                  <Image 
                    className={styles.plusIcon} 
                    width={24} 
                    height={24} 
                    alt="Plus" 
                    src="/assets/icons/plus.svg" 
                  />
                </div>
              </div>
            </>
          )}
        </div>
        {/* Main Chat Area */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 24, minWidth: 0}}>
          {/* Header */}
          <div style={{marginBottom: 24}}>
            <div className={styles.header}>
              <div className={styles.iconNameDefault}>
                <div className={styles.navigationText}>
                  <Image 
                    className={styles.smileyIcon} 
                    width={36} 
                    height={36} 
                    alt="Beth's Assistant" 
                    src="/assets/smiley.svg" 
                  />
                </div>
                <div className={styles.navigationText1}>
                  <div className={styles.name}>Beth's Assistant</div>
                </div>
              </div>
              <div className={styles.dateTime}>
                <div className={styles.navigationText2}>
                  <div className={styles.name}>{timeDisplay.weekday}</div>
                </div>
                <div className={styles.navigationText2}>
                  <div className={styles.name}>{timeDisplay.date}</div>
                </div>
                <div className={styles.navigationText2}>
                  <div className={styles.time}>{timeDisplay.time}</div>
                </div>
              </div>
            </div>
          </div>
          {/* Suggestions */}
          <div style={{display: 'flex', flexDirection: 'column', gap: 24, padding: '0 48px'}}>
            {showSuggestions ? (
              <>
                <div className={styles.greeting}>
                  <div className={styles.greetingText}>
                    Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 17 ? 'Afternoon' : 'Evening'} Beth! What can I help you with today?
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '24px', // 24px gap between rows from Figma specs
                  width: '100%',
                  maxWidth: '912px', // 2 × 433px + 48px gap
                  margin: '0 auto',
                  padding: '0 48px' // Maintain grid margins
                }}>
                  {/* First row */}
                  <div style={{
                    display: 'flex',
                    gap: '48px', // 48px gap between cards from Figma specs
                    justifyContent: 'center'
                  }}>
                    {suggestions.slice(0, 2).map((suggestion, i) => (
                      <SuggestionCard
                        key={`row1-${i}`}
                        text={suggestion}
                        shapeVariant={suggestionShapes[i]}
                        onClick={() => handleSuggestionClick(suggestion)}
                      />
                    ))}
                  </div>
                  
                  {/* Second row */}
                  <div style={{
                    display: 'flex',
                    gap: '48px', // 48px gap between cards from Figma specs
                    justifyContent: 'center'
                  }}>
                    {suggestions.slice(2, 4).map((suggestion, i) => (
                      <SuggestionCard
                        key={`row2-${i}`}
                        text={suggestion}
                        shapeVariant={suggestionShapes[i + 2]}
                        onClick={() => handleSuggestionClick(suggestion)}
                      />
                    ))}
                  </div>
                  
                  {/* Third row */}
                  <div style={{
                    display: 'flex',
                    gap: '48px', // 48px gap between cards from Figma specs
                    justifyContent: 'center'
                  }}>
                    {suggestions.slice(4, 6).map((suggestion, i) => (
                      <SuggestionCard
                        key={`row3-${i}`}
                        text={suggestion}
                        shapeVariant={suggestionShapes[i + 4]}
                        onClick={() => handleSuggestionClick(suggestion)}
                      />
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                padding: '20px',
                overflowY: 'auto',
                maxHeight: '400px'
              }}>
                {messages.map((message) => (
                  <div key={message.id} style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: message.sender === 'user' ? '#000' : '#f7f7f7',
                    color: message.sender === 'user' ? '#fff' : '#000',
                    alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '80%'
                  }}>
                    {message.text}
                  </div>
                ))}
                {isLoading && (
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: '#f7f7f7',
                    color: '#666',
                    alignSelf: 'flex-start',
                    maxWidth: '80%'
                  }}>
                    Thinking...
                  </div>
                )}
              </div>
            )}
          </div>
          {/* Chat Messages (scrollable) */}
          <div style={{flex: 1, overflowY: 'auto', margin: '24px 0'}}>
            {/* ...chat messages... */}
          </div>
          {/* Chat Input */}
          <div style={{padding: '0 48px 0 48px'}}>
            <ChatInput />
          </div>
        </div>
      </div>
    </div>
  );
};

export default FunctionalChatInterface; 