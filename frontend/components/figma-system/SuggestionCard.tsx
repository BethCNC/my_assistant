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
        'outline-none',
        className
      )}
      style={{
        width: '433px', // Fill (433px) from Figma
        height: '64px', // 64px height from CSS
        borderRadius: styles.borderRadius || '4px',
        padding: '0px 12px 0px 0px', // Exact padding from CSS
        background: styles.background,
        border: styles.border,
        boxShadow: styles.boxShadow,
        fontSize: '18px', // 18px from CSS
        fontFamily: 'Mabry Pro',
        fontWeight: 500,
        color: styles.textColor,
        gap: '12px', // 12px gap from CSS
        alignItems: 'center',
        justifyContent: 'flex-start',
        boxSizing: 'border-box',
      }}
      {...props}
    >
      {/* Shape wrapper - exact from CSS */}
      <div
        className="flex-shrink-0 flex items-center justify-center overflow-hidden"
        style={{
          alignSelf: 'stretch', // Full height
          backgroundColor: styles.shapeColor,
          borderRight: styles.shapeBorder,
          padding: '12px',
          width: currentState === 'focus' ? '60px' : 'auto', // 60px width on focus from CSS
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

      {/* Text content - exact from CSS */}
      <div
        style={{
          flex: 1,
          position: 'relative',
          lineHeight: '22px', // 22px line height from CSS
          fontWeight: 500,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          color: styles.textColor,
        }}
      >
        {text}
      </div>

      {/* Arrow icon - exact from CSS */}
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
            height: '66.56%', // From CSS
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
            size={30.5} // 30.5 × 21.3 from CSS
            color={styles.iconColor}
          />
        </div>
      </div>
    </button>
  )
}

export default SuggestionCard