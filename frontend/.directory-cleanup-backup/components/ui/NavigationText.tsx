import React, { useState } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'

// Navigation text variants from Figma documentation
export type NavigationTextWord = 'day' | 'date' | 'time' | 'name' | 'smiley'
export type NavigationTextState = 'default' | 'hover'

interface NavigationTextProps {
  word: NavigationTextWord
  state?: NavigationTextState
  children?: React.ReactNode
  className?: string
  onClick?: () => void
}

/**
 * Navigation Text Component - Based on Figma design system
 * Uses actual smiley SVG from /assets/smiley.svg
 * 
 * Measurements from Figma:
 * - All text: Mabry Pro Black 32px (font-weight: 900)  
 * - Color: neutral/10 (#f7f7f7) - NOT white
 * - Individual hover effects with gradient background
 * - Smiley: 36px × 36px vector graphic
 * 
 * Variants and Properties:
 * - word: day, date, time, name, smiley
 * - state: default, hover
 * - Hover state applies gradient text effect
 */
export function NavigationText({ 
  word, 
  state = 'default',
  children, 
  className,
  onClick 
}: NavigationTextProps) {
  const [isHovered, setIsHovered] = useState(state === 'hover')

  // Get content based on word type
  const getContent = () => {
    if (children) return children
    
    switch (word) {
      case 'day':
        return 'FRIDAY'
      case 'date':
        return 'JUNE 6, 2025'
      case 'time':
        return '11:25 AM'
      case 'name':
        return "BETH'S ASSISTANT"
      case 'smiley':
        return null // Will render smiley icon
      default:
        return children
    }
  }

  // Get hover styles with gradient effect
  const getHoverStyles = () => {
    if (isHovered) {
      return {
        background: designTokens.gradients.rainbow,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        color: 'transparent',
        textShadow: '0 4px 12px rgba(255, 255, 255, 0.3)',
      }
    }
    return {
      color: designTokens.colors.neutral[10], // #f7f7f7 from Figma
    }
  }

  // Render smiley icon using actual SVG file
  if (word === 'smiley') {
    return (
      <div
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={onClick}
        className={cn(
          'cursor-pointer transition-all duration-400 relative',
          className
        )}
        style={{
          width: 36,
          height: 36,
        }}
      >
        {/* Use gradient smiley when hovered, regular when not */}
        {isHovered ? (
          <Image
            src="/assets/smiley-gradient.svg"
            alt="Smiley gradient"
            width={36}
            height={36}
            className="absolute inset-0"
          />
        ) : (
          <Image
            src="/assets/smiley.svg"
            alt="Smiley"
            width={36}
            height={36}
            className="absolute inset-0"
            style={{
              filter: `brightness(0) saturate(100%) invert(97%) sepia(3%) saturate(106%) hue-rotate(169deg) brightness(100%) contrast(93%)` // Convert to neutral[10] color
            }}
          />
        )}
      </div>
    )
  }

  return (
    <span
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      className={cn(
        'font-primary uppercase cursor-pointer transition-all duration-400',
        'text-[32px] leading-[32px] font-black', // Exact measurements from Figma
        className
      )}
      style={{
        fontFamily: designTokens.fonts.primary,
        letterSpacing: '1.2px',
        ...getHoverStyles(),
      }}
    >
      {getContent()}
    </span>
  )
}

export default NavigationText
