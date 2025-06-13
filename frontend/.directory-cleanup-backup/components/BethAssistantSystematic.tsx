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
 * Built with systematic components from Figma design system
 * Uses actual SVG assets with random shape generation
 */
export default function BethAssistant() {
  const [inputValue, setInputValue] = useState('')
  const [activeMCPTab, setActiveMCPTab] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

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

  // Dynamic suggestion cards that change over time
  const [suggestionCards, setSuggestionCards] = useState([
    { text: 'I would like to know about design tokens' },
    { text: 'How do I create a component library?' },
    { text: 'What are the best Figma plugins?' },
    { text: 'Help me implement responsive design' },
    { text: 'Explain design system architecture' },
    { text: 'Guide me through Figma to code workflow' },
  ])

  // Auto-rotate suggestions every 15 seconds to show random shapes
  useEffect(() => {
    const interval = setInterval(() => {
      const allSuggestions = [
        'I would like to know about design tokens',
        'How do I create a component library?',
        'What are the best Figma plugins?',
        'Help me implement responsive design',
        'Explain design system architecture',
        'Guide me through Figma to code workflow',
        'Tell me about color theory in design',
        'How to organize design files effectively?',
        'Best practices for component naming',
        'Accessibility in design systems',
        'Responsive design principles',
        'Component testing strategies',
        'Design system documentation',
        'Figma auto-layout best practices',
        'Creating scalable design systems',
        'Typography in digital design',
      ]
      
      // Shuffle and pick 6 random suggestions
      const shuffled = allSuggestions.sort(() => 0.5 - Math.random())
      const newSuggestions = shuffled.slice(0, 6).map(text => ({ text }))
      setSuggestionCards(newSuggestions)
    }, 15000) // Change every 15 seconds

    return () => clearInterval(interval)
  }, [])

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
          {/* Left Sidebar */}
          <div style={{ marginLeft: `${grid.margin}px` }}>
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
            />
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* MCP Server Connection Tabs */}
            <div 
              className="flex gap-3 mb-6"
              style={{
                marginLeft: `${grid.margin}px`,
                marginRight: `${grid.margin}px`,
                marginTop: `${designTokens.spacing.lg}px`,
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

            {/* Greeting */}
            <div 
              className="text-center mb-6"
              style={{
                marginLeft: `${grid.margin}px`,
                marginRight: `${grid.margin}px`,
              }}
            >
              <h1
                style={{
                  fontSize: designTokens.fontSizes['3xl'],
                  fontWeight: 400,
                  color: designTokens.colors.white,
                  margin: 0,
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                  fontFamily: designTokens.fonts.greeting,
                  lineHeight: 1.2,
                }}
              >
                Good Morning Beth! What can I help you with today?
              </h1>
            </div>

            {/* Suggestion Cards - WITH RANDOM SHAPES */}
            <div 
              className="grid grid-cols-2 gap-6 flex-1 content-start"
              style={{
                marginLeft: `${grid.margin}px`,
                marginRight: `${grid.margin}px`,
              }}
            >
              {suggestionCards.map((card, index) => (
                <SuggestionCard
                  key={`${card.text}-${index}`} // Key includes text to trigger shape changes
                  text={card.text}
                  state={index === 1 ? 'state3' : index === 2 ? 'focus' : 'default'}
                  onClick={() => {
                    console.log('Suggestion clicked:', card.text)
                    setInputValue(card.text)
                  }}
                  randomizeShape={true} // Enable random shape changes
                />
              ))}
            </div>

            {/* Input Area */}
            <div 
              className="mt-auto"
              style={{
                marginLeft: `${grid.margin}px`,
                marginRight: `${grid.margin}px`,
                marginBottom: `${designTokens.spacing.lg}px`,
              }}
            >
              <ChatInput
                value={inputValue}
                onChange={setInputValue}
                onSend={(message) => {
                  console.log('Message sent:', message)
                  // Here you would handle sending the message
                  setInputValue('')
                }}
                onAttachFiles={() => {
                  console.log('Attach files clicked')
                }}
                onAttachImages={() => {
                  console.log('Attach images clicked')
                }}
              />
            </div>
          </div>
        </div>

        {/* Optional: Show notification about auto-rotating suggestions */}
        <div 
          className="fixed bottom-4 right-4 bg-black/70 backdrop-blur-md text-white px-3 py-2 rounded-md text-sm"
          style={{ fontSize: '12px' }}
        >
          🎲 Suggestions auto-rotate every 15s with random shapes
        </div>
      </div>
    </>
  )
}
