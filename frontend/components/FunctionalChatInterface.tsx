'use client';

import React, { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { useChat } from '@/hooks/use-chat';
import { apiClient } from '@/lib/api';
import styles from './ChatInterface.module.css';

const FunctionalChatInterface = () => {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [conversations, setConversations] = useState<any[]>([]);
  const [toolStatuses, setToolStatuses] = useState<{[key: string]: boolean}>({});
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const tools = ['Notion', 'Figma', 'Github', 'Email', 'Calendar'];
  const suggestions = [
    "I would like to know about design tokens",
    "Help me organize my tasks in Notion", 
    "Show me recent GitHub activity",
    "What's on my calendar today?",
    "Create a new task for tomorrow",
    "Search my Figma files"
  ];

  // Check tool connection status
  useEffect(() => {
    const checkToolStatuses = async () => {
      const statuses: {[key: string]: boolean} = {};
      
      try {
        const notionResponse = await apiClient.request('/api/notion/health');
        statuses.Notion = notionResponse.status === 200;
      } catch { statuses.Notion = false; }
      
      try {
        const figmaResponse = await apiClient.request('/api/figma/health');
        statuses.Figma = figmaResponse.status === 200;
      } catch { statuses.Figma = false; }
      
      try {
        const githubResponse = await apiClient.request('/api/github/health');
        statuses.Github = githubResponse.status === 200;
      } catch { statuses.Github = false; }
      
      // Email and Calendar would need separate implementation
      statuses.Email = false;
      statuses.Calendar = false;
      
      setToolStatuses(statuses);
    };
    
    checkToolStatuses();
  }, []);

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

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    setShowSuggestions(false);
    await sendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleSuggestionClick = async (suggestion: string) => {
    setShowSuggestions(false);
    await sendMessage(suggestion);
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
          <div className={styles.sidebar}>
            <div className={styles.recentChats}>
              <div className={styles.labelText}>
                <div className={styles.newChatButton}>Recent Chats</div>
              </div>
              <div className={styles.leadIcon}>
                <Image 
                  className={styles.arrowIcon} 
                  width={31} 
                  height={21} 
                  alt="Arrow" 
                  src="/assets/icon-arrow.svg" 
                />
              </div>
            </div>
            
            <div className={styles.leftColumn}>
              <div className={styles.recentChats1}>
                {conversations.length > 0 ? (
                  conversations.slice(0, 9).map((conv, i) => (
                    <div key={conv.id || i} className={styles.chatHistory}>
                      <div className={styles.chatHistory1}>
                        <div className={styles.howCanI}>
                          {conv.title || conv.preview || `Conversation ${i + 1}`}
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
            }}>
              <div className={styles.labelText}>
                <b className={styles.newChatButton2}>New Chat</b>
              </div>
              <div className={styles.icons}>
                <Image 
                  className={styles.plusIcon} 
                  width={32} 
                  height={32} 
                  alt="Plus" 
                  src="/assets/icon-plus.svg" 
                />
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className={styles.mainContainer1}>
            <div className={styles.contentContainer}>
              <div className={styles.container}>
                {/* Tool Buttons */}
                <div className={styles.buttonContainer}>
                  {tools.map((tool) => (
                    <div key={tool} className={styles.toolButton} style={{
                      position: 'relative'
                    }}>
                      <div className={styles.labelText2}>
                        <b className={styles.notion}>{tool}</b>
                      </div>
                      {/* Connection status indicator */}
                      <div style={{
                        position: 'absolute',
                        top: '8px',
                        right: '8px',
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: toolStatuses[tool] ? '#00ff00' : '#ff6600'
                      }} />
                    </div>
                  ))}
                </div>

                {/* Show suggestions or chat messages */}
                {showSuggestions ? (
                  <>
                    <div className={styles.greeting}>
                      <div className={styles.greetingText}>
                        Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 17 ? 'Afternoon' : 'Evening'} Beth!
                      </div>
                    </div>
                    <div className={styles.suggestionParent}>
                      {suggestions.map((suggestion, i) => (
                        <div 
                          key={i} 
                          className={styles[`suggestion${i === 0 ? '' : i}`]}
                          onClick={() => handleSuggestionClick(suggestion)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className={styles.shapeWrapper}>
                            <div className={styles.suggestionShapes}>
                              <Image 
                                className={styles.vectorIcon} 
                                width={32} 
                                height={32} 
                                alt="Shape" 
                                src="/assets/star.svg" 
                              />
                            </div>
                          </div>
                          <div className={styles.iWouldLike}>{suggestion}</div>
                          <div className={styles.icons}>
                            <Image 
                              className={styles.arrowIcon1} 
                              width={31} 
                              height={21} 
                              alt="Arrow" 
                              src="/assets/icon-arrow.svg" 
                            />
                          </div>
                        </div>
                      ))}
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

              {/* Chat Input - keeping exact same styling and position */}
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
    </div>
  );
};

export default FunctionalChatInterface; 