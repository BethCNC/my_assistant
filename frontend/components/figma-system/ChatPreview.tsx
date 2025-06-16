import React from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'

interface ChatPreviewProps {
  message: string
  onClick?: () => void
  className?: string
  isCollapsed?: boolean
}

/**
 * Chat Preview Component - Fixed to match screenshot layout
 * 
 * Shows chat history items in the sidebar with proper truncation
 * and hover effects. Matches the layout shown in your screenshots.
 */
export function ChatPreview({ 
  message, 
  onClick,
  className,
  isCollapsed = false
}: ChatPreviewProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center text-left w-full transition-all duration-200',
        'hover:bg-white/10 rounded-sm cursor-pointer',
        className
      )}
      style={{
        width: isCollapsed ? 82 : 262, // Fit within sidebar bounds
        minHeight: 40, // Minimum height for touch targets
        padding: '8px 12px', // Comfortable padding
        fontSize: '14px', // Smaller font for better fit
        fontFamily: designTokens.fonts.primary,
        fontWeight: '400',
        color: designTokens.colors.neutral[40], // #404040 gray text
        textAlign: 'left',
        marginBottom: '4px', // Small gap between items
      }}
    >
      <span 
        className="truncate"
        style={{
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          width: '100%',
          lineHeight: '1.2',
        }}
      >
        {message}
      </span>
    </button>
  )
}

export default ChatPreview