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

  // Enhanced dynamic suggestions based on context
  const getContextualSuggestions = () => {
    const baseTopics = [
      'design tokens and system components',
      'organizing tasks and projects in Notion', 
      'recent GitHub activity and pull requests',
      'calendar events and upcoming meetings',
      'creating new tasks and reminders',
      'searching and managing Figma files',
      'analyzing project progress and metrics',
      'setting up automation workflows'
    ];

    // Add context-based suggestions if we have chat history
    const contextualSuggestions = [];
    
    if (conversations.length > 0) {
      contextualSuggestions.push(
        'Continue our previous conversation',
        'Summarize recent chat topics'
      );
    }
    
    // Mix base topics with contextual ones
    const allSuggestions = [...contextualSuggestions, ...baseTopics];
    
    // Return 6 suggestions with varied phrasing
    return allSuggestions.slice(0, 6).map(topic => {
      const starters = [
        'I would like to know about',
        'Help me with',
        'Show me information about',
        'Can you explain',
        'I need assistance with',
        'Tell me about'
      ];
      const starter = starters[Math.floor(Math.random() * starters.length)];
      return `${starter} ${topic}`;
    });
  };

  const [suggestions, setSuggestions] = useState(getContextualSuggestions());

  // Generate random shapes ensuring no duplicates
  const generateRandomShapes = (): SuggestionShapeVariant[] => {
    const shapes: SuggestionShapeVariant[] = [1, 2, 3, 4, 5, 6, 7];
    const selected: SuggestionShapeVariant[] = [];
    
    while (selected.length < 6) {
      const randomIndex = Math.floor(Math.random() * shapes.length);
      const shape = shapes[randomIndex];
      if (!selected.includes(shape)) {
        selected.push(shape);
      }
    }
    
    return selected;
  };

  const [suggestionShapes, setSuggestionShapes] = useState(generateRandomShapes());

  // Update suggestions when conversations change
  useEffect(() => {
    setSuggestions(getContextualSuggestions());
    setSuggestionShapes(generateRandomShapes());
  }, [conversations]);

  // Load conversations on mount
  useEffect(() => {
    const loadConversations = async () => {
      const response = await apiClient.getConversations();
      if (response.data && response.data.chats) {
        setConversations(response.data.chats);
      } else if (response.data && Array.isArray(response.data)) {
        setConversations(response.data);
      }
    };
    loadConversations();
  }, []);

  // Function to load a specific chat
  const handleChatClick = async (chatId: string) => {
    const response = await apiClient.getChatHistory(chatId);
    if (response.data && response.data.chat) {
      // Load the chat messages and switch to chat view
      const chatData = response.data.chat;
      // You can implement message loading here if needed
      setShowSuggestions(false);
    }
  };

  // Function to format chat title for display
  const formatChatTitle = (chat: any) => {
    if (chat.title && chat.title !== 'undefined') {
      return chat.title.length > 30 ? chat.title.substring(0, 30) + '...' : chat.title;
    }
    if (chat.preview) {
      return chat.preview.length > 30 ? chat.preview.substring(0, 30) + '...' : chat.preview;
    }
    return 'Untitled Chat';
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    setShowSuggestions(false);
    await sendMessage(inputValue.trim());
    setInputValue('');
    
    // Reload conversations to update recent chats
    const response = await apiClient.getConversations();
    if (response.data && response.data.chats) {
      setConversations(response.data.chats);
    }
  };

  const handleSuggestionClick = async (suggestion: string) => {
    setShowSuggestions(false);
    await sendMessage(suggestion);
    
    // Reload conversations to update recent chats
    const response = await apiClient.getConversations();
    if (response.data && response.data.chats) {
      setConversations(response.data.chats);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = () => {
    const now = new Date();
    return now.toLocaleString('en-US', {
      weekday: 'long',
      month: 'long', 
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).split(', ');
  };

  const [weekday, date, time] = formatTime();

  return (
    <div className={styles.chatContainer}>
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
              <div className={styles.name}>{weekday}</div>
            </div>
            <div className={styles.navigationText2}>
              <div className={styles.name}>{date}</div>
            </div>
            <div className={styles.navigationText2}>
              <div className={styles.time}>{time}</div>
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
                      Array.from({ length: 9 }, (_, i) => (
                        <div key={i} className={styles.chatHistory}>
                          <div className={styles.chatHistory1}>
                            <div className={styles.howCanI}>No recent chats</div>
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
                  setSuggestionShapes(generateRandomShapes());
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
          <div className={styles.mainContainer1}>
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

            {/* Chat Input - moved outside contentContainer to be a sibling */}
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
  );
};

export default FunctionalChatInterface; 