'use client';

import React, { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import styles from './ChatInterface.module.css';
import { db } from '../utils/firebase';
import {
  collection,
  addDoc,
  query,
  orderBy,
  onSnapshot,
  serverTimestamp,
  Timestamp
} from 'firebase/firestore';

const CHAT_ID = 'default'; // For now, use a single chat session

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  createdAt: Timestamp | null;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Listen for real-time updates from Firebase
  useEffect(() => {
    console.log('Setting up Firestore listener for path:', `chats/${CHAT_ID}/messages`);
    const q = query(
      collection(db, 'chats', CHAT_ID, 'messages'),
      orderBy('createdAt', 'asc')
    );
    
    const unsubscribe = onSnapshot(q, (snapshot) => {
      console.log('Firestore snapshot received, docs count:', snapshot.docs.length);
      const newMessages = snapshot.docs.map(doc => {
        console.log('Message doc:', doc.id, doc.data());
        return {
          id: doc.id,
          ...doc.data()
        } as Message;
      });
      setMessages(newMessages);
      
      // Hide suggestions if we have messages
      if (newMessages.length > 0) {
        setShowSuggestions(false);
      }
    }, (error) => {
      console.error('Firestore listener error:', error);
    });

    return () => unsubscribe();
  }, []);

  // Send message to Firebase
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    console.log('Sending message:', inputValue.trim());
    console.log('Firebase db object:', db);
    console.log('Collection path:', `chats/${CHAT_ID}/messages`);
    
    setIsLoading(true);
    setShowSuggestions(false);
    
    try {
      const docRef = await addDoc(collection(db, 'chats', CHAT_ID, 'messages'), {
        text: inputValue.trim(),
        sender: 'user',
        createdAt: serverTimestamp()
      });
      console.log('Message sent successfully with ID:', docRef.id);
      console.log('Full document path:', docRef.path);
      
      setInputValue('');
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Error details:', {
        code: (error as any)?.code,
        message: (error as any)?.message,
        stack: (error as any)?.stack
      });
      alert('Error sending message: ' + (error as any)?.message);
    } finally {
      setIsLoading(false);
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

  // Sample suggestions
  const suggestions = [
    'Tell me about design tokens and system components',
    'Show me information about organizing projects',
    'Can you explain recent GitHub activity',
    'Can you explain calendar events and meetings',
    'I need assistance with creating new tasks',
    'Can you explain searching and managing files'
  ];

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
      if (window.innerWidth <= 768) {
        setIsSidebarCollapsed(true); // Collapse sidebar on mobile by default
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div className="glass-dark" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 'var(--spacing-3) var(--spacing-4)',
        color: 'var(--color-neutral-white)',
        flexShrink: 0,
        minHeight: '60px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-3)'
        }}>
          <Image 
            width={32} 
            height={32} 
            alt="Beth's Assistant" 
            src="/assets/smiley.svg" 
          />
          <span className="text-on-glass" style={{
            fontSize: '18px',
            fontWeight: '500',
            fontFamily: 'var(--font-mabry-pro)'
          }}>Beth's Assistant</span>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-4)',
          fontSize: '14px',
          fontFamily: 'var(--font-mabry-pro)'
        }}>
          <span className="text-on-glass">{timeDisplay.weekday}</span>
          <span className="text-on-glass">{timeDisplay.date}</span>
          <span className="text-on-glass">{timeDisplay.time}</span>
        </div>
      </div>

      <div style={{
        display: 'flex',
        flex: 1,
        minHeight: 0,
        overflow: 'hidden'
      }}>
        {/* Mobile Overlay */}
        {isMobile && !isSidebarCollapsed && (
          <div 
            className={`mobile-overlay ${!isSidebarCollapsed ? 'active' : ''}`}
            onClick={() => setIsSidebarCollapsed(true)}
          />
        )}

        {/* Sidebar */}
        <div 
          className={`glass-dark ${isMobile ? `sidebar-mobile ${!isSidebarCollapsed ? 'open' : ''}` : ''}`}
          style={{
            width: isMobile ? '280px' : (isSidebarCollapsed ? '0px' : '280px'),
            minWidth: isMobile ? '280px' : (isSidebarCollapsed ? '0px' : '280px'),
            color: 'var(--color-neutral-white)',
            display: 'flex',
            flexDirection: 'column',
            transition: isMobile ? 'transform 0.3s ease' : 'width 0.3s ease',
            overflow: 'hidden',
            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
            ...(isMobile ? {
              position: 'fixed',
              top: '60px',
              left: '0',
              bottom: '0',
              zIndex: 1000,
              transform: isSidebarCollapsed ? 'translateX(-100%)' : 'translateX(0)'
            } : {})
          }}
        >
          {/* Sidebar Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 'var(--spacing-4)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <span className="text-on-glass" style={{ 
              fontWeight: '500',
              fontFamily: 'var(--font-mabry-pro)'
            }}>Recent Chats</span>
            <button 
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-neutral-white)',
                cursor: 'pointer',
                padding: 'var(--spacing-1)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-mabry-pro)'
              }}
            >
              ←
            </button>
          </div>
          
          {/* Chat History */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: 'var(--spacing-2)'
          }}>
            {[
              'How can I better update my design tokens',
              'How can I better organize my projects', 
              'How can I better manage my calendar',
              'How can I better track my tasks',
              'How can I better use GitHub workflows',
              'How can I better structure my files',
              'How can I better automate my work',
              'How can I better sync my tools',
              'How can I better plan my schedule'
            ].map((text, i) => (
              <div key={i} style={{
                padding: 'var(--spacing-3)',
                margin: 'var(--spacing-1) 0',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                fontSize: '14px',
                lineHeight: '1.4',
                fontFamily: 'var(--font-mabry-pro)',
                color: 'var(--color-neutral-white)',
                transition: 'background 0.2s ease',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }}
              >
                {text}
              </div>
            ))}
          </div>

          {/* New Chat Button */}
          <div style={{
            padding: 'var(--spacing-4)',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <button 
              onClick={() => {
                setMessages([]);
                setShowSuggestions(true);
                setInputValue('');
              }}
              className="btn-primary"
              style={{
                width: '100%',
                padding: 'var(--spacing-3)',
                borderRadius: 'var(--radius-md)',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--spacing-2)',
                fontFamily: 'var(--font-mabry-pro)'
              }}
            >
              + New Chat
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="glass-effect" style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
          overflow: 'hidden',
          margin: 'var(--spacing-2)',
          borderRadius: 'var(--radius-xl)'
        }}>
          {/* Mobile Menu Button */}
          {isMobile && (
            <div style={{
              padding: 'var(--spacing-3) var(--spacing-4)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <button 
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  padding: 'var(--spacing-2) var(--spacing-3)',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  fontSize: '14px',
                  color: 'var(--color-neutral-white)',
                  fontFamily: 'var(--font-mabry-pro)'
                }}
              >
                ☰ Menu
              </button>
            </div>
          )}

          {/* Chat Content */}
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minHeight: 0,
            overflow: 'hidden'
          }}>
            {showSuggestions && messages.length === 0 ? (
              // Welcome Screen
              <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 'var(--spacing-5)',
                overflowY: 'auto'
              }}>
                <h1 className="heading-primary" style={{
                  fontSize: 'clamp(24px, 4vw, 48px)',
                  fontWeight: '400',
                  margin: '0 0 var(--spacing-8) 0',
                  textAlign: 'center',
                  lineHeight: '1.2'
                }}>
                  Good Morning Beth! What can I help you with today?
                </h1>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: 'var(--spacing-3)',
                  width: '100%',
                  maxWidth: '800px',
                  padding: '0 var(--spacing-4)'
                }}>
                  {suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      onClick={() => {
                        setInputValue(suggestion);
                        setShowSuggestions(false);
                      }}
                      className="glass-effect"
                      style={{
                        padding: 'var(--spacing-4)',
                        borderRadius: 'var(--radius-lg)',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        fontSize: '14px',
                        lineHeight: '1.4',
                        color: 'var(--color-neutral-white)',
                        fontFamily: 'var(--font-mabry-pro)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = 'var(--shadow-glow)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0px)';
                        e.currentTarget.style.boxShadow = '';
                      }}
                    >
                      {suggestion}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Chat Messages
              <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-4)',
                padding: 'var(--spacing-5)',
                overflowY: 'auto',
                minHeight: 0
              }}>
                {messages.map((message) => (
                  <div key={message.id} style={{
                    padding: 'var(--spacing-3) var(--spacing-4)',
                    borderRadius: 'var(--radius-lg)',
                    backgroundColor: message.sender === 'user' 
                      ? 'var(--gradient-blue)' 
                      : 'rgba(255, 255, 255, 0.9)',
                    color: message.sender === 'user' 
                      ? 'var(--color-neutral-white)' 
                      : 'var(--color-neutral-50)',
                    alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                    wordWrap: 'break-word',
                    fontSize: '15px',
                    lineHeight: '1.5',
                    fontFamily: 'var(--font-mabry-pro)',
                    boxShadow: message.sender === 'user' ? 'var(--shadow-button)' : '0 2px 8px rgba(0,0,0,0.1)'
                  }}>
                    {message.text}
                  </div>
                ))}
                {isLoading && (
                  <div style={{
                    padding: 'var(--spacing-3) var(--spacing-4)',
                    borderRadius: 'var(--radius-lg)',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    color: 'var(--color-neutral-30)',
                    alignSelf: 'flex-start',
                    maxWidth: '85%',
                    fontSize: '15px',
                    fontFamily: 'var(--font-mabry-pro)'
                  }}>
                    Thinking...
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div style={{
            flexShrink: 0,
            padding: isMobile ? 'var(--spacing-3)' : 'var(--spacing-4)',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div className="glass-effect" style={{
              display: 'flex',
              alignItems: 'flex-end',
              gap: isMobile ? 'var(--spacing-2)' : 'var(--spacing-3)',
              padding: isMobile ? 'var(--spacing-2)' : 'var(--spacing-3)',
              borderRadius: 'var(--radius-lg)',
              transition: 'border-color 0.2s ease'
            }}>
              {/* Text Input */}
              <div style={{ flex: 1 }}>
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me a question..."
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    minHeight: isMobile ? '40px' : '44px',
                    maxHeight: isMobile ? '100px' : '120px',
                    border: 'none',
                    outline: 'none',
                    background: 'transparent',
                    resize: 'none',
                    fontSize: '16px',
                    fontFamily: 'var(--font-mabry-pro)',
                    color: 'var(--color-neutral-white)',
                    lineHeight: '1.5'
                  }}
                  onFocus={(e) => {
                    e.currentTarget.parentElement!.parentElement!.style.borderColor = 'var(--color-brand-blue-base)';
                  }}
                  onBlur={(e) => {
                    e.currentTarget.parentElement!.parentElement!.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                  }}
                />
              </div>

              {/* Controls */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: isMobile ? 'var(--spacing-1)' : 'var(--spacing-2)'
              }}>
                {/* Attachment buttons - Hide on very small screens */}
                {!isMobile && (
                  <>
                    <button style={{
                      background: 'none',
                      border: 'none',
                      padding: 'var(--spacing-2)',
                      cursor: 'pointer',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: '44px',
                      minWidth: '44px',
                      color: 'var(--color-neutral-white)'
                    }}>
                      📎
                    </button>
                    <button style={{
                      background: 'none',
                      border: 'none',
                      padding: 'var(--spacing-2)',
                      cursor: 'pointer',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: '44px',
                      minWidth: '44px',
                      color: 'var(--color-neutral-white)'
                    }}>
                      📷
                    </button>
                  </>
                )}

                {/* Character count - Hide on mobile */}
                {!isMobile && (
                  <span style={{
                    fontSize: '12px',
                    color: 'rgba(255, 255, 255, 0.6)',
                    minWidth: '50px',
                    textAlign: 'right',
                    fontFamily: 'var(--font-mabry-pro)'
                  }}>
                    {inputValue.length}/1000
                  </span>
                )}

                {/* Send button */}
                <button 
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="btn-primary"
                  style={{
                    padding: isMobile ? 'var(--spacing-3) var(--spacing-4)' : 'var(--spacing-2) var(--spacing-4)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '14px',
                    fontWeight: '500',
                    minWidth: isMobile ? '70px' : '60px',
                    minHeight: '44px',
                    opacity: inputValue.trim() && !isLoading ? 1 : 0.5,
                    fontFamily: 'var(--font-mabry-pro)'
                  }}
                >
                  {isLoading ? '...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;