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
  style?: React.CSSProperties
}

/**
 * New Chat Button Component - Fixed icon size based on visual feedback
 * 
 * From Figma anatomy: lead icon (INSTANCE) - 32px × 32px
 * But visual feedback suggests icon appears too small
 * Adjusting for better visual balance
 */
export function NewChatButton({ 
  size = 'full', 
  state = 'default',
  onClick,
  disabled = false,
  className,
  style 
}: NewChatButtonProps) {
  const [currentState, setCurrentState] = useState(state)

  // Get exact dimensions from Figma measurements
  const getDimensions = () => {
    switch (size) {
      case 'collapsed':
        return { width: 96, height: 64 } // Exact from Figma
      case 'full':
      default:
        return { width: 244, height: 64 } // Exact from Figma
    }
  }

  // Get styles based on state from Figma documentation
  const getStateStyles = () => {
    switch (currentState) {
      case 'hover':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC
          borderColor: designTokens.colors.blue, // #2180EC
          color: designTokens.colors.neutral[10], // #F7F7F7
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: false,
          useGradient: false,
        }
      case 'focus':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC
          borderColor: designTokens.colors.blue, // #2180EC
          color: designTokens.colors.neutral[10], // #F7F7F7
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: true,
          useGradient: false,
        }
      case 'active':
        return {
          backgroundColor: designTokens.colors.blue, // Fallback
          borderColor: designTokens.colors.blue, // #2180EC stroke
          color: designTokens.colors.neutral[10], // #F7F7F7
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: false,
          useGradient: true, // Use the blue gradient
        }
      default:
        return {
          backgroundColor: designTokens.colors.black, // #000000
          borderColor: designTokens.colors.black, // #000000
          color: designTokens.colors.neutral[10], // #F7F7F7
          iconColor: designTokens.colors.neutral[10],
          showFocusRing: false,
          useGradient: false,
        }
    }
  }

  const dimensions = getDimensions()
  const stateStyles = getStateStyles()

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => !disabled && setCurrentState('hover')}
      onMouseLeave={() => !disabled && setCurrentState(state)}
      onFocus={() => !disabled && setCurrentState('focus')}
      onBlur={() => !disabled && setCurrentState(state)}
      onMouseDown={() => !disabled && setCurrentState('active')}
      onMouseUp={() => !disabled && setCurrentState('hover')}
      className={cn(
        'relative inline-flex items-center justify-center',
        'font-primary font-bold transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'outline-none',
        className
      )}
      style={{
        ...dimensions,
        borderRadius: '8px', // Slightly more rounded for better visual
        padding: '16px',
        fontSize: '28px', // Exact from Figma: Mabry Pro Bold 28px
        fontFamily: designTokens.fonts.primary,
        fontWeight: 700,
        // Use gradient for active state, solid color for others
        background: stateStyles.useGradient ? designTokens.gradients.blue : stateStyles.backgroundColor,
        backgroundColor: stateStyles.useGradient ? undefined : stateStyles.backgroundColor,
        color: stateStyles.color,
        border: `1px solid ${stateStyles.borderColor}`,
        gap: size === 'full' ? '42px' : '0', // Exact 42px gap from Figma measurements
        ...style, // Allow override styles
      }}
    >
      {/* Focus ring */}
      {stateStyles.showFocusRing && (
        <div
          style={{
            position: 'absolute',
            top: '-3px',
            left: '-3px',
            right: '-3px',
            bottom: '-3px',
            borderRadius: '11px', // 8px + 3px offset
            border: `2px solid ${designTokens.colors.blue}`,
            pointerEvents: 'none',
            zIndex: 1,
          }}
        />
      )}

      {/* Show "New Chat" text only in full size */}
      {size === 'full' && (
        <span style={{ 
          fontSize: '28px', // Exact from Figma: Mabry Pro Bold 28px
          fontWeight: 700,
          color: stateStyles.color,
        }}>
          New Chat
        </span>
      )}
      
      {/* Plus icon - 32px from Figma specification */}
      <Icons 
        icon="plus" 
        size={32} // Exact 32px from Figma measurements
        color={stateStyles.iconColor}
      />
    </button>
  )
}

export default NewChatButton