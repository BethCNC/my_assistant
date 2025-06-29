import React, { useState } from 'react'
import { designTokens } from '@/lib/design-tokens'

// Import all the components
import { Sidebar } from './figma-system/Sidebar'
import { NavigationText } from './figma-system/NavigationText'
import { ToolButton } from './figma-system/ToolButton'
import { SuggestionCard } from './figma-system/SuggestionCard'
import { ChatInput } from './figma-system/ChatInput'

/**
 * Beth Assistant Main Layout - Pixel Perfect Figma Implementation
 * 
 * Exact measurements from Figma desktop layout:
 * - Overall: 1440px × 900px fixed desktop layout
 * - Sidebar: 270px width (collapsed: 90px)
 * - Main content area: Responsive width based on sidebar state
 * - Header: Full width with proper spacing and dark background
 * - Content area: Proper gaps and alignment
 * - Background: Rainbow gradient from assets/gradient.png
 * - Layout grid: 48px margins, 24px gutters
 */

interface ChatHistoryItem {
  id: string
  title: string
}

interface AttachedFile {
  id: string
  name: string
  type: 'image' | 'file'
  progress?: number
  thumbnailVariant?: '01' | '02' | '03' | '04'
}

export default function BethAssistantMain() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([])
  
  // Sample data matching Figma
  const recentChats: ChatHistoryItem[] = [
    { id: '1', title: 'How can I better update my design tokens' },
    { id: '2', title: 'How can I better update my design tokens' },
    { id: '3', title: 'How can I better update my design tokens' },
    { id: '4', title: 'How can I better update my design tokens' },
    { id: '5', title: 'How can I better update my design tokens' },
    { id: '6', title: 'How can I better update my design tokens' },
    { id: '7', title: 'How can I better update my design tokens' },
    { id: '8', title: 'How can I better update my design tokens' },
    { id: '9', title: 'How can I better update my design tokens' },
  ]

  const suggestionTexts = [
    "I would like to know about design tokens",
    "I would like to know about design tokens", 
    "I would like to know about design tokens",
    "I would like to know about design tokens",
    "I would like to know about design tokens",
    "I would like to know about design tokens",
  ]

  const handleNewChat = () => {
    console.log('New chat started')
  }

  const handleChatSelect = (chatId: string) => {
    console.log('Selected chat:', chatId)
  }

  const handleToggleCollapse = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  const handleSuggestionClick = (text: string) => {
    setChatInput(text)
  }

  const handleSendMessage = (message: string) => {
    console.log('Sending message:', message)
    setChatInput('')
  }

  const handleToolClick = (tool: string) => {
    console.log('Tool clicked:', tool)
  }

  return (
    <div
      style={{
        width: '1440px', // Exact from Figma
        height: '900px', // Exact from Figma
        position: 'relative',
        overflow: 'hidden',
        backgroundImage: designTokens.gradients.rainbow, // Rainbow gradient background
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: 'flex',
        fontFamily: designTokens.fonts.primary,
        margin: '0 auto', // Center the layout
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          flexShrink: 0,
          zIndex: 10,
        }}
      >
        <Sidebar
          variant={sidebarCollapsed ? 'collapsed' : 'default'}
          recentChats={recentChats.map(chat => chat.title)}
          onNewChat={handleNewChat}
          onChatSelect={handleChatSelect}
          onToggleCollapse={handleToggleCollapse}
        />
      </div>

      {/* Main Content Area */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100%',
          paddingLeft: '24px', // Gap between sidebar and main content
          paddingRight: '48px', // Right margin from Figma layout grid
          paddingTop: '24px',
          paddingBottom: '24px',
        }}
      >
        {/* Header Section */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 32px', // Padding inside header
            backgroundColor: 'rgba(23, 23, 23, 0.9)', // Semi-transparent dark background
            borderRadius: '8px',
            marginBottom: '24px',
          }}
        >
          {/* Left side - Assistant name and smiley */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
            }}
          >
            <NavigationText word="smiley" state="default" />
            <NavigationText word="name" state="default" />
          </div>

          {/* Right side - Date and time */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '24px',
            }}
          >
            <NavigationText word="day" state="default" />
            <NavigationText word="date" state="default" />
            <NavigationText word="time" state="default" />
          </div>
        </div>

        {/* Tool Buttons Row */}
        <div
          style={{
            display: 'flex',
            gap: '12px', // Gap between tool buttons from Figma
            marginBottom: '24px',
            justifyContent: 'flex-start',
            flexWrap: 'wrap',
          }}
        >
          <ToolButton
            variant="notion"
            state="default"
            onClick={() => handleToolClick('notion')}
          />
          <ToolButton
            variant="figma"
            state="default"
            onClick={() => handleToolClick('figma')}
          />
          <ToolButton
            variant="github"
            state="default"
            onClick={() => handleToolClick('github')}
          />
          <ToolButton
            variant="email"
            state="default"
            onClick={() => handleToolClick('email')}
          />
          <ToolButton
            variant="calendar"
            state="default"
            onClick={() => handleToolClick('calendar')}
          />
        </div>

        {/* Suggestion Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr', // 2 columns exactly like Figma
            gap: '24px', // 24px gap between cards
            marginBottom: '32px',
            justifyItems: 'start', // Left align the cards
            maxWidth: '900px', // Constrain width for better layout
          }}
        >
          {suggestionTexts.map((text, index) => (
            <SuggestionCard
              key={index}
              text={text}
              onClick={() => handleSuggestionClick(text)}
              shapeVariant={(index % 7 + 1) as any}
            />
          ))}
        </div>

        {/* Chat Input - Bottom positioned */}
        <div
          style={{
            marginTop: 'auto', // Push to bottom
            display: 'flex',
            justifyContent: 'flex-start', // Left align like in Figma
          }}
        >
          <ChatInput
            value={chatInput}
            onChange={setChatInput}
            onSend={(message, attachments) => {
              console.log('Sending message:', message, attachments)
              setChatInput('')
            }}
            placeholder="Ask me a question..."
            maxLength={1000}
          />
        </div>
      </div>
    </div>
  )
}
