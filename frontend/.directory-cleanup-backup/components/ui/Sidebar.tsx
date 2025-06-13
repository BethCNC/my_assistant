import React from 'react'
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
  onChatSelect?: (chatId: string, index: number) => void
  className?: string
}

/**
 * Sidebar Component - Based on Figma design system
 * 
 * Measurements from Figma:
 * - default: 270px × 792px
 * - collapsed: 90px × 792px
 * - Background: neutral/10 with 20% opacity (#F7F7F7)
 * - "recent chats" text: neutral/50 (#171717)
 * - New Chat Button text: Mabry Pro Regular 24px, color: neutral/10 (#F7F7F7)
 * 
 * Nested Instances:
 * - lead icon: 32px × 32px
 * - Chat Preview: 270px × 50px (default) or 90px × 50px (collapsed)
 * - new chat button: 270px × 64px (default) or 90px × 64px (collapsed)
 */
export function Sidebar({ 
  variant = 'default', 
  recentChats = [],
  onNewChat,
  onChatSelect,
  className 
}: SidebarProps) {
  const isCollapsed = variant === 'collapsed'
  
  // Get dimensions based on variant from Figma
  const getDimensions = () => {
    if (isCollapsed) {
      return { width: 90, height: 792 }
    }
    return { width: 270, height: 792 }
  }

  const dimensions = getDimensions()

  return (
    <div
      className={cn(
        // Base styles
        'flex flex-col gap-1 overflow-hidden',
        className
      )}
      style={{
        width: dimensions.width,
        height: dimensions.height,
        backgroundColor: `${designTokens.colors.neutral[10]}33`, // 20% opacity (#F7F7F733)
        padding: isCollapsed ? '4px' : '4px 8px', // Different padding for collapsed vs default
      }}
    >
      {/* Header with lead icon and "recent chats" text */}
      <div 
        className="flex items-center justify-between mb-4"
        style={{
          padding: isCollapsed ? '12px 4px' : '12px',
        }}
      >
        {/* Lead icon - 32px × 32px from Figma */}
        <Icons 
          icon="plus" 
          size={32} 
          color={designTokens.colors.neutral[50]}
        />
        
        {/* Show "recent chats" text only in default variant */}
        {!isCollapsed && (
          <span
            style={{
              fontSize: '16px',
              fontFamily: designTokens.fonts.primary,
              color: designTokens.colors.neutral[50], // #171717 from Figma
              fontWeight: 400,
            }}
          >
            recent chats
          </span>
        )}
      </div>

      {/* Chat Preview List */}
      <div 
        className="flex-1 flex flex-col gap-1 overflow-y-auto"
        style={{
          padding: isCollapsed ? '0' : '0 4px',
        }}
      >
        {recentChats.map((chat, index) => (
          <ChatPreview
            key={index}
            message={chat}
            onClick={() => onChatSelect?.(chat, index)}
            className={cn(
              // Adjust width for collapsed state
              isCollapsed && 'w-[90px]'
            )}
          />
        ))}
      </div>

      {/* New Chat Button */}
      <div 
        className="mt-auto"
        style={{
          padding: isCollapsed ? '8px 4px' : '8px',
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
