'use client';

import React, { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { useChat } from '@/hooks/use-chat';
import { apiClient } from '@/lib/api';
import { SuggestionCard } from './figma-system/SuggestionCard';
import { SuggestionShapeVariant } from './figma-system/SuggestionShapes';
import styles from './ChatInterface.module.css';

const FunctionalChatInterface = () => {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
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

  // Enhanced dynamic suggestions based on context
  const getContextualSuggestions = () => {
    // If we have chat history, generate suggestions based on recent topics
    if (conversations.length > 0) {
      const recentTopics = conversations.slice(0, 5).map(conv => {
        const title = formatChatTitle(conv);
        // Extract key topics from chat titles to generate follow-up suggestions
        if (title.toLowerCase().includes('design')) {
          return 'Continue discussing design system improvements';
        } else if (title.toLowerCase().includes('notion') || title.toLowerCase().includes('organize')) {
          return 'Help me organize more projects in Notion';
        } else if (title.toLowerCase().includes('github') || title.toLowerCase().includes('code')) {
          return 'Show me recent GitHub activity and updates';
        } else if (title.toLowerCase().includes('calendar') || title.toLowerCase().includes('schedule')) {
          return 'Review my upcoming calendar events';
        } else if (title.toLowerCase().includes('task') || title.toLowerCase().includes('todo')) {
          return 'Help me create and manage new tasks';
        } else if (title.toLowerCase().includes('figma') || title.toLowerCase().includes('file')) {
          return 'Find and organize my Figma files';
        } else {
          // Generic follow-up based on the conversation
          return `Continue our conversation about ${title.toLowerCase().replace(/^how can i better /, '').replace(/\?$/, '')}`;
        }
      });

      // Add some general contextual suggestions
      const contextualSuggestions = [
        'Summarize my recent chat topics',
        'What were we discussing last time?',
        ...recentTopics
      ];

      // Fill remaining slots with general suggestions if needed
      const generalSuggestions = [
        'Tell me about my upcoming appointments',
        'Show me my recent GitHub commits',
        'Help me plan my day',
        'What tasks do I have pending?',
        'Check my Notion workspace updates',
        'Review my calendar for this week'
      ];

      const allSuggestions = [...contextualSuggestions, ...generalSuggestions];
      return allSuggestions.slice(0, 6);
    }

    // Default suggestions when no chat history exists
    const defaultSuggestions = [
      'Tell me about design tokens and system components',
      'Show me information about organizing projects',
      'Can you explain recent GitHub activity',
      'Can you explain calendar events and meetings',
      'I need assistance with creating new tasks',
      'Can you explain searching and managing files'
    ];
    
    return defaultSuggestions;
  };

  const [suggestions, setSuggestions] = useState(getContextualSuggestions());

  // Use fixed shapes to prevent hydration mismatch (server vs client random differences)
  const suggestionShapes: SuggestionShapeVariant[] = [3, 1, 2, 7, 4, 6];

  // Update suggestions when conversations change
  useEffect(() => {
    setSuggestions(getContextualSuggestions());
  }, [conversations]);

  // Load conversations on mount
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const response = await apiClient.getConversations();
        if (response.data && (response.data as any).chats) {
          setConversations((response.data as any).chats);
        } else if (response.data && Array.isArray(response.data)) {
          setConversations(response.data);
        }
      } catch (error) {
        // Silently handle offline mode - conversations will show placeholders
        console.log('API offline, using placeholder conversations');
      }
    };
    loadConversations();
  }, []);

  // Function to load a specific chat
  const handleChatClick = async (chatId: string) => {
    try {
      const response = await apiClient.getChatHistory(chatId);
      if (response.data && response.data.chat) {
        // Load the chat messages and switch to chat view
        const chatData = response.data.chat;
        // You can implement message loading here if needed
        setShowSuggestions(false);
      }
    } catch (error) {
      // Silently handle offline mode
      console.log('API offline, cannot load chat history');
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    setShowSuggestions(false);
    await sendMessage(inputValue.trim());
    setInputValue('');
    
    // Try to reload conversations, but don't fail if offline
    try {
      const response = await apiClient.getConversations();
      if (response.data && (response.data as any).chats) {
        setConversations((response.data as any).chats);
      }
    } catch (error) {
      // Silently handle offline mode
      console.log('API offline, conversations not updated');
    }
  };

  const handleSuggestionClick = async (suggestion: string) => {
    setShowSuggestions(false);
    await sendMessage(suggestion);
    
    // Try to reload conversations, but don't fail if offline
    try {
      const response = await apiClient.getConversations();
      if (response.data && (response.data as any).chats) {
        setConversations((response.data as any).chats);
      }
    } catch (error) {
      // Silently handle offline mode
      console.log('API offline, conversations not updated');
    }
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
    <div className={styles.appWrapper}>
      <div className={styles.content}>
        {/* Header */}
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
        <div className={styles.mainContainer}>
          {/* Sidebar */}
          <div className={`${styles.sidebar} ${isSidebarCollapsed ? styles.sidebarCollapsed : ''}`}>
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
                      conversations.slice(0, 9).map((conv, i) => (
                        <div 
                          key={conv.id || i} 
                          className={styles.chatHistory}
                          onClick={() => handleChatClick(conv.id)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className={styles.chatHistory1}>
                            <div className={styles.howCanI}>
                              {formatChatTitle(conv)}
                            </div>
                          </div>
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
          {/* Main Content */}
          <div className={styles.rightContainer}>
            <div className={styles.contentContainer}>
              <div className={styles.container}>
                {/* Show suggestions or chat messages */}
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
                        backgroundColor: message.role === 'user' ? '#000' : '#f7f7f7',
                        color: message.role === 'user' ? '#fff' : '#000',
                        alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%'
                      }}>
                        {message.content}
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
            </div>
            {/* Chat Input at bottom, not fixed */}
            <div className={styles.chatInput}>
              <div className={styles.chatInputDefault}>
                <div className={styles.textarea}>
                  <div className={styles.input}>
                    <textarea
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask me a question..."
                      disabled={isLoading}
                      style={{
                        width: '100%',
                        height: '100%',
                        border: 'none',
                        outline: 'none',
                        background: 'transparent',
                        resize: 'none',
                        fontSize: '16px',
                        fontWeight: '500',
                        color: inputValue ? '#000' : '#808080',
                        fontFamily: 'inherit'
                      }}
                    />
                  </div>
                </div>
                <div className={styles.controls1}>
                  <div className={styles.controlsLeft}>
                    <div className={styles.iconButtons}>
                      <div className={styles.icons6}>
                        <Image 
                          className={styles.filesIcon} 
                          width={22} 
                          height={24} 
                          alt="Files" 
                          src="/assets/icon-paperclip.svg" 
                        />
                      </div>
                    </div>
                    <div className={styles.iconButtons}>
                      <div className={styles.icons6}>
                        <Image 
                          className={styles.imagesIcon} 
                          width={24} 
                          height={20} 
                          alt="Images" 
                          src="/assets/icon-camera.svg" 
                        />
                      </div>
                    </div>
                  </div>
                  <div className={styles.controlsRight}>
                    <div className={styles.charCount}>{inputValue.length}/1000</div>
                    <div 
                      className={styles.iconButtons} 
                      onClick={handleSendMessage}
                      style={{
                        opacity: inputValue.trim() && !isLoading ? 1 : 0.5,
                        cursor: inputValue.trim() && !isLoading ? 'pointer' : 'not-allowed'
                      }}
                    >
                      <div className={styles.icons6}>
                        <Image 
                          className={styles.sendIcon} 
                          width={24} 
                          height={22} 
                          alt="Send" 
                          src="/assets/icon-send.svg" 
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FunctionalChatInterface; 