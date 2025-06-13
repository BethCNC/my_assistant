import React, { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { Icons } from './Icons'
import { SuggestionShapes, getRandomShape, SuggestionShapeVariant } from './SuggestionShapes'

// Suggestion states from Figma documentation
export type SuggestionState = 'default' | 'state3' | 'focus'

interface SuggestionCardProps {
  text: string
  state?: SuggestionState
  onClick?: () => void
  className?: string
  randomizeShape?: boolean // New prop to control shape randomization
  shape?: SuggestionShapeVariant // Allow manual shape override
}

/**
 * Suggestion Card Component - Based on Figma design system
 * Uses actual SVG files from /assets/shapes/svg/
 * 
 * Measurements from Figma:
 * - Size: 433px × 60px
 * - Text: Mabry Pro Medium 18px
 * - Color: neutral/50 (#171717)
 * - Border radius: 12px
 * - Nested instances: suggestion shapes (32px × 32px), Icons (32px × 32px)
 * 
 * States from Figma:
 * - default: neutral/10 background, neutral/50 stroke, neutral/50 shape
 * - state3: neutral/10 background, neutral/50 stroke, Orange shape (#FF7D59)
 * - focus: neutral/10 background, Blue stroke (#2180EC), Blue shape (#2180EC)
 * 
 * Features:
 * - Random shape selection on text change
 * - Shape color changes based on state
 */
export function SuggestionCard({ 
  text, 
  state = 'default',
  onClick,
  className,
  randomizeShape = true,
  shape: fixedShape,
  ...props
}: SuggestionCardProps) {
  const [currentState, setCurrentState] = useState(state)
  const [currentShape, setCurrentShape] = useState<SuggestionShapeVariant>(
    fixedShape || getRandomShape()
  )

  // Randomize shape when text changes (if randomization is enabled)
  useEffect(() => {
    if (randomizeShape && !fixedShape) {
      setCurrentShape(getRandomShape())
    }
  }, [text, randomizeShape, fixedShape])

  // Get styles based on state from Figma documentation
  const getStateStyles = () => {
    switch (currentState) {
      case 'state3':
        return {
          background: designTokens.colors.neutral[10], // #f7f7f7
          border: `1px solid ${designTokens.colors.neutral[50]}`, // #171717
          shapeColor: designTokens.colors.orange, // #FF7D59
          iconColor: designTokens.colors.neutral[50], // #171717
        }
      case 'focus':
        return {
          background: designTokens.colors.neutral[10], // #f7f7f7
          border: `1px solid ${designTokens.colors.blue}`, // #2180EC
          shapeColor: designTokens.colors.blue, // #2180EC
          iconColor: designTokens.colors.neutral[50], // #171717
        }
      default:
        return {
          background: designTokens.colors.neutral[10], // #f7f7f7
          border: `1px solid ${designTokens.colors.neutral[50]}`, // #171717
          shapeColor: designTokens.colors.neutral[50], // #171717
          iconColor: designTokens.colors.neutral[50], // #171717
        }
    }
  }

  const styles = getStateStyles()

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setCurrentState('focus')}
      onMouseLeave={() => setCurrentState(state)}
      onFocus={() => setCurrentState('focus')}
      onBlur={() => setCurrentState(state)}
      className={cn(
        // Base styles
        'inline-flex items-center gap-3 text-left transition-all duration-300',
        'hover:scale-[1.02] hover:shadow-lg',
        'outline-none', // Remove default focus outline
        className
      )}
      style={{
        width: 433, // 433px width from Figma
        height: 60, // 60px height from Figma
        borderRadius: '12px', // 12px border radius from Figma
        padding: '12px', // Calculated from measurements
        background: styles.background,
        border: styles.border,
        fontSize: '18px', // Mabry Pro Medium 18px from Figma
        fontFamily: designTokens.fonts.primary,
        fontWeight: 500, // Medium weight
        color: designTokens.colors.neutral[50], // #171717 from Figma
      }}
      {...props}
    >
      {/* Shape wrapper - 32px × 32px from Figma */}
      <div
        className="flex-shrink-0 rounded-md flex items-center justify-center"
        style={{
          width: 32,
          height: 32,
          backgroundColor: styles.shapeColor,
          border: `1px solid ${styles.shapeColor}`,
        }}
      >
        {/* Suggestion shape using actual SVG files */}
        <SuggestionShapes 
          shape={currentShape}
          size={24} // Slightly smaller than container for padding
          color={designTokens.colors.white} // White shape inside colored background
        />
      </div>

      {/* Text content */}
      <span className="flex-1 leading-tight">
        {text}
      </span>

      {/* Arrow icon - 32px × 32px from Figma */}
      <Icons 
        icon="arrow" 
        size={32} 
        color={styles.iconColor}
      />
    </button>
  )
}

export default SuggestionCard
