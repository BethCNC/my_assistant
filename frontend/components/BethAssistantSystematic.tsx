'use client'

import React, { useState, useEffect } from 'react'
import { designTokens } from '@/lib/design-tokens'

// Import our systematic components from figma-system
import { NavigationText } from '@/components/figma-system/NavigationText'
import { ToolButton } from '@/components/figma-system/ToolButton'
import { SuggestionCard } from '@/components/figma-system/SuggestionCard'
import { Sidebar } from '@/components/figma-system/Sidebar'
import { ChatInput } from '@/components/figma-system/ChatInput'

// 12-column grid system (48px margins, 24px gutters)
const grid = {
  margin: 48,
  gutter: 24,
  columns: 12,
  containerWidth: 1280 - (48 * 2),
  columnWidth: (1280 - (48 * 2) - (24 * 11)) / 12,
}

/**
 * Beth's Assistant - Main Component
 * Updated with improved components that match exact Figma specifications
 */
export default function BethAssistant() {
  const [inputValue, setInputValue] = useState('')
  const [activeMCPTab, setActiveMCPTab] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [chatHistory, setChatHistory] = useState<string[]>([])

  // Sample data
  const recentChats = [
    'How can I better update my design system?',
    'What are design tokens?',
    'How do I implement glassmorphism?',
    'Best practices for component libraries',
    'Figma to code workflow tips',
    'Component testing strategies',
    'Design system documentation',
  ]

  // Static suggestion cards - shapes only change when chat history updates
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
  }

  const handleSend = (message: string, attachments: { images: any[], files: any[] }) => {
    console.log('Message sent:', message, attachments)
    // Add to chat history to trigger shape updates
    setChatHistory([...chatHistory, message])
    setInputValue('')
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
          font-weight: 700;
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
          background: designTokens.gradients.rainbow,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          fontFamily: designTokens.fonts.primary,
        }}
      >
        {/* Header */}
        <div 
          className="flex justify-between items-center"
          style={{
            margin: `${designTokens.spacing.lg}px ${grid.margin}px 0 ${grid.margin}px`,
            background: designTokens.colors.black,
            color: designTokens.colors.white,
            padding: `${designTokens.spacing.lg}px`,
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

        <div className="flex flex-1 h-[calc(100vh-116px)] max-h-[684px]">
          {/* Left Sidebar - Fixed 24px gap from header */}
          <div style={{ 
            marginLeft: `${grid.margin}px`,
            marginTop: `${grid.gutter}px`, // 24px gap from header
            height: '100%', // Ensure sidebar takes full height
            display: 'flex',
          }}>
            <Sidebar
              variant={sidebarCollapsed ? 'collapsed' : 'default'}
              recentChats={recentChats}
              onNewChat={() => {
                console.log('New chat clicked')
                setInputValue('')
              }}
              onChatSelect={(chat, index) => {
                console.log('Chat selected:', chat, index)
                setInputValue(chat)
              }}
              onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
            />
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* MCP Server Connection Tabs - Fixed 24px gap from sidebar */}
            <div 
              className="flex gap-3"
              style={{
                marginLeft: `${grid.gutter}px`, // 24px gap from sidebar (matches Figma)
                marginRight: `${grid.margin}px`,
                marginTop: `${grid.gutter}px`, // 24px gap from header to match sidebar
                marginBottom: '10px',
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

            {/* Greeting - Fixed 24px gap from sidebar */}
            <div 
              className="text-center"
              style={{
                marginLeft: `${grid.gutter}px`, // 24px gap from sidebar (matches Figma)
                marginRight: `${grid.margin}px`,
                paddingTop: '12px',
                paddingBottom: '12px',
                marginBottom: '10px',
              }}
            >
              <h1
                style={{
                  fontSize: '42px',
                  fontWeight: 500,
                  color: designTokens.colors.neutral[50],
                  margin: 0,
                  fontFamily: 'Behind The Nineties',
                  lineHeight: '42px',
                  letterSpacing: '0%',
                  textAlign: 'center',
                }}
              >
                Good Morning Beth! What can I help you with today?
              </h1>
            </div>

            {/* Suggestion Cards - Fixed 24px gap from sidebar */}
            <div 
              className="grid grid-cols-2 gap-6 flex-1 content-start"
              style={{
                marginLeft: `${grid.gutter}px`, // 24px gap from sidebar (matches Figma)
                marginRight: `${grid.margin}px`,
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

            {/* Input Area - Fixed 24px gap from sidebar */}
            <div 
              className="mt-auto"
              style={{
                marginLeft: `${grid.gutter}px`, // 24px gap from sidebar (matches Figma)
                marginRight: `${grid.margin}px`,
                marginBottom: `${designTokens.spacing.lg}px`,
              }}
            >
              <ChatInput
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSend}
              />
            </div>
          </div>
        </div>

        {/* Updated notification */}
        <div 
          className="fixed bottom-4 right-4 bg-black/70 backdrop-blur-md text-white px-3 py-2 rounded-md text-sm"
          style={{ fontSize: '12px' }}
        >
          🎯 Suggestions shapes update when you send messages
        </div>
      </div>
    </>
  )
}