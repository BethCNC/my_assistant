import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { Icons } from './Icons'
import { SuggestionShapes, SuggestionShapeVariant } from './SuggestionShapes'

// Suggestion states from Figma documentation
export type SuggestionState = 'default' | 'hover' | 'focus'

interface SuggestionCardProps {
  text: string
  onClick?: () => void
  className?: string
  shapeVariant?: SuggestionShapeVariant
}

/**
 * Suggestion Card Component - Updated to match exact Figma hover effects
 * 
 * Key behavior from CSS:
 * - Background stays #F7F7F7 (white) on hover
 * - Shape background changes to orange (#FF7D59) on hover
 * - Shape background changes to blue (#2180EC) on focus
 * - Special shadow effects on hover
 * - Border changes on focus (blue)
 */
export function SuggestionCard({ 
  text, 
  onClick,
  className,
  shapeVariant = 1,
  ...props
}: SuggestionCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  // Get current state for styling
  const getCurrentState = (): SuggestionState => {
    if (isFocused) return 'focus'
    if (isHovered) return 'hover'
    return 'default'
  }

  const currentState = getCurrentState()

  // Get styles based on state from CSS specifications
  const getStateStyles = () => {
    switch (currentState) {
      case 'hover':
        return {
          // Background stays white with special shadow
          background: '#F7F7F7', // Background stays the same
          border: '2px solid #171717', // Border stays the same
          boxShadow: '0px 0px 100px #FEEBE5, 0px 0px 1px 4px rgba(255, 255, 255, 0.1), 0px -2px 2px rgba(0, 0, 0, 0.25) inset, 0px 2px 1px rgba(255, 255, 255, 0.25) inset',
          textColor: '#171717', // Text stays black
          shapeColor: '#FF7D59', // Orange shape background
          shapeBorder: '2px solid #171717', // Shape border
          shapeIconColor: '#FFFFFF', // White shape icon
          iconColor: '#171717', // Black arrow
        }
      case 'focus':
        return {
          background: '#F7F7F7', // Background stays white
          border: '2px solid #2180EC', // Blue border on focus
          borderRadius: '6px', // Slightly more rounded on focus
          boxShadow: 'none',
          textColor: '#171717', // Text stays black
          shapeColor: '#2180EC', // Blue shape background
          shapeBorder: '1px solid #2180EC', // Blue shape border
          shapeIconColor: '#FFFFFF', // White shape icon
          iconColor: '#171717', // Black arrow
        }
      default:
        return {
          background: '#F7F7F7', // White background
          border: '2px solid #171717', // Black border
          borderRadius: '4px',
          boxShadow: 'none',
          textColor: '#171717', // Black text
          shapeColor: '#171717', // Black shape background
          shapeBorder: '2px solid #171717', // Black shape border
          shapeIconColor: '#FFFFFF', // White shape icon
          iconColor: '#171717', // Black arrow
        }
    }
  }

  const styles = getStateStyles()

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      className={cn(
        'inline-flex items-center text-left transition-all duration-200',
        'outline-none cursor-pointer',
        className
      )}
      style={{
        width: '433px', // Fixed width
        height: '64px', // Fixed height
        display: 'flex',
        alignItems: 'center',
        borderRadius: styles.borderRadius || '4px',
        padding: '0px 12px 0px 0px',
        background: styles.background,
        border: styles.border,
        boxShadow: styles.boxShadow,
        fontSize: '18px',
        fontFamily: 'Mabry Pro',
        fontWeight: 500,
        color: styles.textColor,
        gap: '12px',
        justifyContent: 'flex-start',
        boxSizing: 'border-box',
        transform: currentState === 'hover' ? 'translateY(-1px)' : 'none',
      }}
      {...props}
    >
      {/* Shape wrapper - fixed size */}
      <div
        className="flex-shrink-0 flex items-center justify-center overflow-hidden"
        style={{
          width: '60px',
          height: '100%',
          backgroundColor: styles.shapeColor,
          borderRight: styles.shapeBorder,
          padding: '12px',
        }}
      >
        <div style={{ width: '32px', height: '32px' }}>
          <SuggestionShapes 
            shape={shapeVariant}
            size={32}
            color={styles.shapeIconColor}
          />
        </div>
      </div>
      {/* Text content - fixed, centered, truncated */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          position: 'relative',
          lineHeight: '22px',
          fontWeight: 500,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          color: styles.textColor,
          height: '100%',
        }}
      >
        {text}
      </div>
      {/* Arrow icon - fixed */}
      <div 
        style={{
          width: '32px',
          position: 'relative',
          height: '32px',
        }}
      >
        <div
          style={{
            position: 'absolute',
            height: '66.56%',
            top: '16.67%',
            bottom: '16.77%',
            left: 'calc(50% - 15.24px)',
            maxHeight: '100%',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icons 
            icon="arrow" 
            size={30.5}
            color={styles.iconColor}
          />
        </div>
      </div>
    </button>
  )
}

export default SuggestionCard