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
 * Sidebar Component - Rewritten to match Figma exactly
 * 
 * From Figma design:
 * - Simple vertical list layout
 * - Semi-transparent background
 * - Chat items with hover states
 * - New Chat button at bottom
 * - Toggle arrow in header
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
  
  // Default chat data for demo (matching Figma)
  const defaultChats = recentChats.length > 0 ? recentChats : [
    'How can I better update my design tokens',
    'What are design tokens?', 
    'How do I implement glassmorphism?',
    'Best practices for component libraries',
    'Figma to code workflow tips',
    'Component testing strategies',
    'Design system documentation',
    'Figma auto-layout best practices',
    'Creating scalable design systems',
  ]

  return (
    <div
      className={cn('flex flex-col', className)}
      style={{
        width: isCollapsed ? '90px' : '270px',
        height: '100%',
        backgroundColor: 'rgba(247, 247, 247, 0.2)', // Semi-transparent from Figma
        borderRadius: '4px',
        padding: '4px', // Small padding around content
        gap: '4px', // Gap between items
      }}
    >
      {/* Header - Recents Chat with toggle arrow */}
      <div
        style={{
          backgroundColor: '#171717', // Dark header background
          borderRadius: '4px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          minHeight: '50px',
        }}
      >
        {!isCollapsed && (
          <span
            style={{
              fontFamily: 'Mabry Pro',
              fontSize: '24px',
              fontWeight: '400',
              color: '#F7F7F7',
            }}
          >
            Recents Chat
          </span>
        )}
        
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
            transform: isCollapsed ? 'rotate(180deg)' : 'none',
            transition: 'transform 0.3s ease',
          }}
        >
          <Icons 
            icon="arrow" 
            size={24}
            color="#F7F7F7"
          />
        </button>
      </div>

      {/* Chat List - Scrollable */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          overflowY: 'auto',
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

      {/* New Chat Button at Bottom */}
      <div
        style={{
          padding: '4px',
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <NewChatButton
          size={isCollapsed ? 'collapsed' : 'full'}
          onClick={onNewChat}
        />
      </div>
    </div>
  )
}

export default Sidebar