'use client'

import React, { useState, useEffect } from 'react'
import { designTokens } from '@/lib/design-tokens'

// Import our systematic components from figma-system
import { NavigationText } from '@/components/figma-system/NavigationText'
import { ToolButton } from '@/components/figma-system/ToolButton'
import { SuggestionCard } from '@/components/figma-system/SuggestionCard'
import { Sidebar } from '@/components/figma-system/Sidebar'
import { ChatInput } from '@/components/figma-system/ChatInput'
import { ChatConversation } from '@/components/figma-system/ChatConversation'

// 12-column grid system from Figma (48px margins, 24px gutters)
const grid = {
  margin: 48, // Outer margins
  gutter: 24, // Gap between elements
  columns: 12,
  containerWidth: 1280 - (48 * 2),
  columnWidth: (1280 - (48 * 2) - (24 * 11)) / 12,
}

/**
 * Beth's Assistant - Main Component
 * Fixed spacing based on your screenshot feedback:
 * - 48px gap between sidebar and right side
 * - Proper 2×3 grid for suggestion cards with 24px gaps
 * - Correct sidebar positioning
 */
export default function BethAssistant() {
  const [inputValue, setInputValue] = useState('')
  const [activeMCPTab, setActiveMCPTab] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [chatHistory, setChatHistory] = useState<string[]>([])
  const [chatMessages, setChatMessages] = useState<any[]>([]) // Store actual chat messages
  const [hasStartedChat, setHasStartedChat] = useState(false) // Track if conversation has started

  // Sample data matching your screenshots
  const recentChats = [
    'How can I better update my design system?',
    'What are design tokens?',
    'How do I implement glassmorphism?',
    'Best practices for component libraries',
    'Figma to code workflow tips',
    'Component testing strategies',
    'Design system documentation',
    'Figma auto-layout best practices',
    'Creating scalable design systems',
  ]

  // Static suggestion cards matching your screenshots
  const suggestions = [
    { text: 'Guide me through Figma to code workflow' },
    { text: 'Accessibility in design systems' },
    { text: 'How to organize design files effectively?' },
    { text: 'Component testing strategies' },
    { text: 'What are the best Figma plugins?' },
    { text: 'Help me implement responsive design' },
  ]

  // Generate suggestion shapes based on chat history length to avoid automatic rotation
  const getSuggestionShapeVariant = (index: number, chatHistoryLength: number) => {
    // Use chat history length as seed for consistent but varied shapes
    return ((index + chatHistoryLength) % 7) + 1
  }

  const handleSuggestionClick = (text: string) => {
    console.log('Suggestion clicked:', text)
    setInputValue(text)
    // Start conversation immediately when suggestion is clicked
    handleSend(text, { images: [], files: [] })
  }

  const handleSend = (message: string, attachments: { images: any[], files: any[] }) => {
    console.log('Message sent:', message, attachments)
    
    if (!message.trim()) return
    
    // Create user message
    const userMessage = {
      id: Date.now().toString(),
      sender: 'Beth',
      message: message,
      timestamp: 'Just now',
      isUser: true
    }
    
    // Add user message
    const newMessages = [...chatMessages, userMessage]
    setChatMessages(newMessages)
    setHasStartedChat(true)
    
    // Add to chat history for sidebar
    setChatHistory([...chatHistory, message])
    setInputValue('')
    
    // Simulate assistant response after a short delay
    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'Assistant',
        message: getAssistantResponse(message),
        timestamp: 'Just now',
        isUser: false
      }
      setChatMessages(prev => [...prev, assistantMessage])
    }, 1000)
  }
  
  // Simple response generator for demo
  const getAssistantResponse = (userMessage: string): string => {
    if (userMessage.toLowerCase().includes('design token')) {
      return 'Design tokens are the visual design atoms of the design system — specifically, they are named entities that store visual design attributes. They help maintain consistency and scalability across your design system.'
    }
    if (userMessage.toLowerCase().includes('figma')) {
      return 'Figma is excellent for design systems! I can help you learn about components, variables, auto-layout, and best practices for organizing your design files. What specific aspect would you like to explore?'
    }
    return 'I can help you with that! Could you tell me more about what specific aspects you\'d like to focus on?'
  }

  const mcpTools = ['notion', 'figma', 'github', 'email', 'calendar'] as const

  return (
    <>
      {/* Font loading */}
      <style jsx global>{`
        @font-face {
          font-family: 'Mabry Pro';
          src: url('/assets/font/MabryPro-Regular.woff') format('woff'),
               url('/assets/font/MabryPro-Regular.ttf') format('truetype');
          font-weight: 400;
          font-style: normal;
          font-display: swap;
        }
        @font-face {
          font-family: 'Mabry Pro';
          src: url('/assets/font/MabryPro-Bold.woff') format('woff'),
               url('/assets/font/MabryPro-Bold.ttf') format('truetype');
          font-weight: 700;
          font-style: normal;
          font-display: swap;
        }
        @font-face {
          font-family: 'Mabry Pro';
          src: url('/assets/font/MabryPro-Black.woff') format('woff'),
               url('/assets/font/MabryPro-Black.ttf') format('truetype');
          font-weight: 900;
          font-style: normal;
          font-display: swap;
        }
        @font-face {
          font-family: 'Behind The Nineties';
          src: url('/assets/font/Behind-The-Nineties-Rg.otf') format('opentype');
          font-weight: 400;
          font-style: normal;
          font-display: swap;
        }
      `}</style>

      <div 
        className="w-screen h-screen max-h-[800px] overflow-hidden flex flex-col"
        style={{ 
          background: `url('/assets/gradient.png')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          fontFamily: designTokens.fonts.primary,
        }}
      >
        {/* Header with exact 48px margins */}
        <div 
          className="flex justify-between items-center"
          style={{
            margin: `${grid.gutter}px ${grid.margin}px 0 ${grid.margin}px`, // 24px top, 48px sides
            background: designTokens.colors.black,
            color: designTokens.colors.white,
            padding: `${grid.gutter}px`, // 24px padding
            height: '76px',
            borderRadius: `${designTokens.radii.sm}px`,
          }}
        >
          {/* Left side - Smiley + Title */}
          <div className="flex items-center gap-3">
            <NavigationText word="smiley" />
            <NavigationText word="name" />
          </div>

          {/* Right side - Date and Time */}
          <div className="flex items-center gap-8">
            <NavigationText word="day" />
            <NavigationText word="date" />
            <NavigationText word="time" />
          </div>
        </div>

        {/* Main content area with proper grid spacing */}
        <div className="flex flex-1" style={{ marginTop: `${grid.gutter}px` }}>
          {/* Left Sidebar - exactly 48px from edge */}
          <div style={{ 
            marginLeft: `${grid.margin}px`, // 48px from screen edge
            marginRight: `${grid.margin}px`, // 48px gap to the right side
            flexShrink: 0, // Don't shrink the sidebar
          }}>
            <Sidebar
              variant={sidebarCollapsed ? 'collapsed' : 'default'}
              recentChats={recentChats}
              onNewChat={() => {
                console.log('New chat clicked')
                // Reset conversation state
                setInputValue('')
                setChatMessages([])
                setHasStartedChat(false)
              }}
              onChatSelect={(chat, index) => {
                console.log('Chat selected:', chat, index)
                setInputValue(chat)
              }}
              onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
            />
          </div>

          {/* Main Content Area - fills remaining space */}
          <div 
            className="flex-1 flex flex-col min-w-0" // min-w-0 prevents flex overflow
            style={{
              marginRight: `${grid.margin}px`, // 48px margin to screen edge
            }}
          >
            {/* MCP Server Connection Tabs */}
            <div 
              className="flex gap-3 flex-wrap" // Added flex-wrap for responsiveness
              style={{
                marginBottom: `${grid.gutter}px`, // 24px gap below
              }}
            >
              {mcpTools.map((tool) => (
                <ToolButton
                  key={tool}
                  variant={tool}
                  state={activeMCPTab === tool ? 'active' : 'default'}
                  onClick={() => {
                    setActiveMCPTab(activeMCPTab === tool ? null : tool)
                    console.log(`${tool} MCP server clicked`)
                  }}
                />
              ))}
            </div>

            {/* Greeting Text - only show when no conversation started */}
            {!hasStartedChat && (
              <div
                style={{
                  marginBottom: `${grid.gutter}px`, // 24px gap below greeting
                  textAlign: 'center',
                }}
              >
                <h1
                  style={{
                    fontFamily: 'Behind The Nineties, serif',
                    fontSize: '48px',
                    fontWeight: '400',
                    color: designTokens.colors.black,
                    margin: 0,
                    textShadow: '2px 2px 4px rgba(0,0,0,0.1)',
                  }}
                >
                  Good Morning Beth! What can I help you with today?
                </h1>
              </div>
            )}

            {/* Content Area - either suggestions or chat conversation */}
            {!hasStartedChat ? (
              // Show suggestion cards when no conversation started
              <div 
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)', // 2 columns
                  gridTemplateRows: 'repeat(3, 1fr)', // 3 rows  
                  gap: `${grid.gutter}px`, // 24px gaps both horizontal and vertical
                  marginBottom: '104px', // CRITICAL: 104px gap from suggestions to chat input
                  flex: 1, // Take remaining space
                  alignContent: 'start', // Align to top
                }}
              >
                {suggestions.map((suggestion, index) => (
                  <SuggestionCard
                    key={index}
                    text={suggestion.text}
                    shapeVariant={getSuggestionShapeVariant(index, chatHistory.length)}
                    onClick={() => handleSuggestionClick(suggestion.text)}
                  />
                ))}
              </div>
            ) : (
              // Show chat conversation when conversation started
              <div 
                style={{
                  flex: 1,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'flex-start',
                  marginBottom: '48px', // Space above chat input
                  paddingTop: '24px', // Small padding from top
                }}
              >
                <ChatConversation 
                  messages={chatMessages}
                />
              </div>
            )}

            {/* Chat Input at bottom */}
            <div>
              <ChatInput
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSend}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  )
}