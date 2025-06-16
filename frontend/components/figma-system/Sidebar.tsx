import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { ChatPreview } from './ChatPreview'
import { NewChatButton } from './NewChatButton'
import { Icons } from './Icons'

// Sidebar variants from Figma documentation
export type SidebarVariant = 'default' | 'collapsed'

interface SidebarProps {
  variant?: SidebarVariant
  recentChats?: string[]
  onNewChat?: () => void
  onChatSelect?: (chat: string, index: number) => void
  onToggleCollapse?: () => void
  className?: string
}

/**
 * Sidebar Component - Fixed based on Figma design and your screenshots
 * 
 * Key fixes:
 * - Proper semi-transparent background
 * - Dark header section with "Recents Chat" text
 * - Correct arrow behavior and positioning
 * - Proper chat preview layout
 * - Integrated New Chat button at bottom
 */
export function Sidebar({ 
  variant = 'default', 
  recentChats = [],
  onNewChat,
  onChatSelect,
  onToggleCollapse,
  className 
}: SidebarProps) {
  const isCollapsed = variant === 'collapsed'
  
  // Default chat data matching your screenshots
  const defaultChats = recentChats.length > 0 ? recentChats : [
    'How can I better update my design system',
    'What are design tokens?',
    'How do I implement glassmorphism?',
    'Best practices for component libraries',
    'Figma to code workflow tips',
    'Component testing strategies',
    'Design system documentation',
    'Figma auto-layout best practices',
    'Creating scalable design systems',
  ]

  // Get exact dimensions from Figma measurements
  const sidebarWidth = isCollapsed ? 90 : 270

  return (
    <div
      className={cn('flex flex-col relative', className)}
      style={{
        width: sidebarWidth,
        height: '100%', // Full height of container
        maxHeight: '680px', // Reasonable max height
        // Semi-transparent background from Figma
        backgroundColor: 'rgba(247, 247, 247, 0.2)',
        borderRadius: '4px',
        overflow: 'hidden',
      }}
    >
      {/* Header Section - Dark background with "Recents Chat" text */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          padding: '12px 16px',
          backgroundColor: designTokens.colors.neutral[50], // Dark background #171717
          minHeight: '48px',
        }}
      >
        {/* Show "Recents Chat" text in default variant */}
        {!isCollapsed && (
          <span
            style={{
              fontFamily: designTokens.fonts.primary,
              fontSize: '20px', // Slightly smaller to fit better
              fontWeight: '400',
              color: designTokens.colors.neutral[10], // White text #F7F7F7
            }}
          >
            Recents Chat
          </span>
        )}
        
        {/* Toggle arrow button */}
        <button
          onClick={onToggleCollapse}
          style={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            // Arrow points left when expanded (to collapse), right when collapsed (to expand)
            transform: isCollapsed ? 'rotate(0deg)' : 'rotate(180deg)',
            transition: 'transform 0.3s ease',
          }}
        >
          <Icons 
            icon="arrow" 
            size={20}
            color={designTokens.colors.neutral[10]} // White arrow
          />
        </button>
      </div>

      {/* Chat Preview List - Scrollable area */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflowY: 'auto',
          padding: '8px 4px',
          // Reserve space for New Chat Button
          paddingBottom: '72px', // Space for button + padding
        }}
      >
        {defaultChats.map((chat, index) => (
          <ChatPreview
            key={`chat-${index}`}
            message={isCollapsed ? 'How...' : chat}
            onClick={() => onChatSelect?.(chat, index)}
            isCollapsed={isCollapsed}
          />
        ))}
      </div>

      {/* New Chat Button - Fixed at bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: '8px',
          left: '8px',
          right: '8px',
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <NewChatButton
          size={isCollapsed ? 'collapsed' : 'full'}
          onClick={onNewChat}
          style={{
            width: isCollapsed ? '74px' : '254px', // Fit within sidebar
            height: '56px',
          }}
        />
      </div>
    </div>
  )
}

export default Sidebar