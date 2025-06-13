import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { Icons } from './Icons'

// New Chat Button variants from Figma documentation
export type NewChatButtonSize = 'full' | 'collapsed'
export type NewChatButtonState = 'default' | 'hover' | 'focus' | 'active'

interface NewChatButtonProps {
  size?: NewChatButtonSize
  state?: NewChatButtonState
  onClick?: () => void
  disabled?: boolean
  className?: string
}

/**
 * New Chat Button Component - Pixel Perfect Figma Implementation
 * 
 * Exact measurements from Figma PDFs:
 * - full: 244px × 64px with "New Chat" text + plus icon
 * - collapsed: 96px × 64px with only plus icon
 * - Text: Mabry Pro Bold 28px, color: #F7F7F7 (neutral/10)
 * - Icon: 32px × 32px plus icon
 * - Border radius: 8px (from measurements)
 * - Padding: 16px (calculated from measurements)
 * 
 * States from Figma image:
 * - default: Black background (#000000), white text
 * - hover: Blue background (#2180EC), white text
 * - focus: Blue background (#2180EC) with focus ring, white text
 * - active: Blue gradient background, white text
 */
export function NewChatButton({ 
  size = 'full', 
  state = 'default',
  onClick,
  disabled = false,
  className 
}: NewChatButtonProps) {
  const [currentState, setCurrentState] = useState(state)

  // Get dimensions based on size from Figma measurements
  const getDimensions = () => {
    switch (size) {
      case 'collapsed':
        return { width: 80, height: 48 } // Smaller to fit in 90px sidebar
      case 'full':
      default:
        return { width: 260, height: 48 } // Smaller to fit in 270px sidebar
    }
  }

  // Get styles based on state from Figma image
  const getStateStyles = () => {
    switch (currentState) {
      case 'hover':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC from Figma
          color: designTokens.colors.neutral[10], // #F7F7F7 from Figma
          border: `1px solid ${designTokens.colors.blue}`,
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: false,
        }
      case 'focus':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC from Figma
          color: designTokens.colors.neutral[10], // #F7F7F7 from Figma
          border: `1px solid ${designTokens.colors.blue}`,
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: true,
        }
      case 'active':
        return {
          background: designTokens.gradients.blue, // Blue gradient: #69DEF2 to #126FD8
          color: designTokens.colors.neutral[10], // #F7F7F7 from Figma
          border: `1px solid ${designTokens.colors.blue}`,
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: false,
        }
      default:
        return {
          backgroundColor: designTokens.colors.black, // #000000 from Figma
          color: designTokens.colors.neutral[10], // #F7F7F7 from Figma
          border: `1px solid ${designTokens.colors.black}`,
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: false,
        }
    }
  }

  const dimensions = getDimensions()
  const stateStyles = getStateStyles()

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setCurrentState('hover')}
      onMouseLeave={() => setCurrentState(state)}
      onFocus={() => setCurrentState('focus')}
      onBlur={() => setCurrentState(state)}
      className={cn(
        // Base styles
        'relative inline-flex items-center justify-center gap-2',
        'font-primary font-bold transition-all duration-300',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'outline-none', // Remove default focus outline
        className
      )}
      style={{
        width: dimensions.width,
        height: dimensions.height,
        borderRadius: '8px', // Exact from Figma measurements
        padding: '12px', // Smaller padding
        fontSize: '20px', // Smaller font size
        fontFamily: designTokens.fonts.primary,
        fontWeight: 700, // Bold
        backgroundColor: stateStyles.backgroundColor,
        background: stateStyles.background || stateStyles.backgroundColor,
        color: stateStyles.color,
        border: stateStyles.border,
      }}
    >
      {/* Focus ring - positioned absolutely like in Figma */}
      {stateStyles.showFocusRing && (
        <div
          style={{
            position: 'absolute',
            top: '-6px',
            left: '-6px',
            right: '-6px',
            bottom: '-6px',
            borderRadius: '14px', // 8px + 6px offset
            border: `4px solid ${designTokens.colors.blue}`,
            zIndex: 1,
          }}
        />
      )}

      {/* Show text only in full size */}
      {size === 'full' && (
        <span>New Chat</span>
      )}
      
      {/* Plus icon - Smaller size */}
      <Icons 
        icon="plus" 
        size={24} 
        color={stateStyles.iconColor}
      />
    </button>
  )
}

export default NewChatButton