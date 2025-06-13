import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'

// Tool button variants from Figma documentation
export type ToolButtonVariant = 'notion' | 'figma' | 'github' | 'email' | 'calendar'
export type ToolButtonState = 'default' | 'hover' | 'focus' | 'active'

interface ToolButtonProps {
  variant: ToolButtonVariant
  state?: ToolButtonState
  onClick?: () => void
  disabled?: boolean
  className?: string
}

/**
 * Tool Button Component - Based on Figma design system
 * 
 * Measurements from Figma:
 * - Size: 154px × 48px (calendar example)
 * - Text: Mabry Pro Bold 20px
 * - Border radius: 6px on all buttons
 * - Padding: 12px top/bottom, 32px left/right
 * 
 * States from Figma:
 * - default: Black background, white text, no border
 * - hover: Blue background (#2180EC), black text, no border  
 * - focus: Blue background (#2180EC), black text, blue border ring
 * - active: Transparent background, black text, no border
 */
export function ToolButton({ 
  variant, 
  state = 'default',
  onClick,
  disabled = false,
  className 
}: ToolButtonProps) {
  const [currentState, setCurrentState] = useState(state)

  // Get button text based on variant
  const getButtonText = () => {
    switch (variant) {
      case 'notion':
        return 'Notion'
      case 'figma':
        return 'Figma'
      case 'github':
        return 'Github'
      case 'email':
        return 'Email'
      case 'calendar':
        return 'Calendar'
      default:
        return variant
    }
  }

  // Get styles based on state from Figma documentation
  const getStateStyles = () => {
    switch (currentState) {
      case 'hover':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC from Figma
          color: designTokens.colors.black,
          border: 'none',
        }
      case 'focus':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC from Figma
          color: designTokens.colors.black,
          border: 'none',
          boxShadow: `0 0 0 2px ${designTokens.colors.blue}`, // Blue border ring
        }
      case 'active':
        return {
          backgroundColor: 'transparent',
          color: designTokens.colors.black,
          border: 'none',
        }
      default:
        return {
          backgroundColor: designTokens.colors.black,
          color: designTokens.colors.white,
          border: 'none',
        }
    }
  }

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
        'inline-flex items-center justify-center text-center',
        'font-primary font-bold transition-all duration-300',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'outline-none', // Remove default focus outline
        className
      )}
      style={{
        borderRadius: '6px', // 6px radius from Figma
        padding: '12px 32px', // 12px top/bottom, 32px left/right from Figma
        fontSize: '20px', // 20px from Figma
        lineHeight: '24px', // 24px line height from Figma
        fontFamily: designTokens.fonts.primary,
        whiteSpace: 'nowrap',
        height: '48px', // 48px height from Figma
        minWidth: 'auto',
        ...stateStyles,
      }}
    >
      {getButtonText()}
    </button>
  )
}

export default ToolButton
