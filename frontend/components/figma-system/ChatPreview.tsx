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
 * Chat Preview Component - Based on Figma design system
 * 
 * Measurements from Figma:
 * - Size: 270px × 50px
 * - Text: Mabry Pro Regular 20px
 * - Color: neutral/40 (#404040)
 * - Padding: 4px, 8px, 12px spacing from measurements
 * 
 * Component: Default
 * - Shows truncated chat message
 * - Hover effect with background and transform
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
        // Base styles
        'flex items-center text-left w-full transition-all duration-200',
        'hover:bg-white/10 hover:translate-x-0.5 hover:opacity-100',
        'rounded-sm cursor-pointer',
        className
      )}
      style={{
        width: isCollapsed ? 90 : 270, // Responsive width
        height: 50, // 50px height from Figma
        padding: '4px 8px 12px', // Padding from Figma measurements
        fontSize: '20px', // Mabry Pro Regular 20px from Figma
        fontFamily: designTokens.fonts.primary,
        color: designTokens.colors.neutral[40], // #404040 from Figma
        opacity: 0.8,
      }}
    >
      {/* Truncate long messages */}
      <span className="truncate">
        {message}
      </span>
    </button>
  )
}

export default ChatPreview