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
 * New Chat Button Component - Based on Figma design system
 * Uses actual plus icon from /assets/icons/plus.svg
 * 
 * Measurements from Figma:
 * - full: 244px × 64px
 * - collapsed: 96px × 64px
 * - Text: Mabry Pro Bold 28px
 * - Color: neutral/10 (#f7f7f7)
 * - Icon: 32px × 32px (lead icon)
 * - Padding: 16px (from measurements)
 * 
 * States from Figma:
 * - default: Black background, white text, black border
 * - hover: Blue background (#2180EC), white text, blue border
 * - focus: Blue background (#2180EC), white text, blue border  
 * - active: Transparent background, white text, blue border
 */
export function NewChatButton({ 
  size = 'full', 
  state = 'default',
  onClick,
  disabled = false,
  className 
}: NewChatButtonProps) {
  const [currentState, setCurrentState] = useState(state)

  // Get dimensions based on size from Figma
  const getDimensions = () => {
    switch (size) {
      case 'collapsed':
        return { width: 96, height: 64 }
      case 'full':
      default:
        return { width: 244, height: 64 }
    }
  }

  // Get styles based on state from Figma documentation
  const getStateStyles = () => {
    switch (currentState) {
      case 'hover':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC from Figma
          color: designTokens.colors.neutral[10], // #f7f7f7 from Figma
          border: `1px solid ${designTokens.colors.blue}`,
          iconColor: designTokens.colors.neutral[10],
        }
      case 'focus':
        return {
          backgroundColor: designTokens.colors.blue, // #2180EC from Figma
          color: designTokens.colors.neutral[10], // #f7f7f7 from Figma
          border: `1px solid ${designTokens.colors.blue}`,
          iconColor: designTokens.colors.neutral[10],
        }
      case 'active':
        return {
          backgroundColor: 'transparent',
          color: designTokens.colors.neutral[10], // #f7f7f7 from Figma
          border: `1px solid ${designTokens.colors.blue}`,
          iconColor: designTokens.colors.neutral[10],
        }
      default:
        return {
          backgroundColor: designTokens.colors.black,
          color: designTokens.colors.neutral[10], // #f7f7f7 from Figma
          border: `1px solid ${designTokens.colors.black}`,
          iconColor: designTokens.colors.neutral[10],
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
        'inline-flex items-center justify-center gap-2',
        'font-primary font-bold transition-all duration-300',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'outline-none', // Remove default focus outline
        className
      )}
      style={{
        width: dimensions.width,
        height: dimensions.height,
        borderRadius: `${designTokens.radii.md}px`, // 8px border radius
        padding: '16px', // 16px padding from Figma measurements
        fontSize: '28px', // Mabry Pro Bold 28px from Figma
        fontFamily: designTokens.fonts.primary,
        backgroundColor: stateStyles.backgroundColor,
        color: stateStyles.color,
        border: stateStyles.border,
      }}
    >
      {/* Lead icon - 32px × 32px from Figma using actual plus.svg */}
      <Icons 
        icon="plus" 
        size={32} 
        color={stateStyles.iconColor}
      />
      
      {/* Show text only in full size */}
      {size === 'full' && (
        <span>New Chat</span>
      )}
    </button>
  )
}

export default NewChatButton