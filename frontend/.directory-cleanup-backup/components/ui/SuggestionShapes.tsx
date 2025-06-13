import React from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

// Shape variants from your assets/shapes/svg folder
export type SuggestionShapeVariant = 1 | 2 | 3 | 4 | 5 | 6 | 7

interface SuggestionShapeProps {
  shape?: SuggestionShapeVariant
  className?: string
  size?: number
  color?: string
  style?: React.CSSProperties
}

/**
 * Suggestion Shapes Component - Based on Figma design system
 * Uses actual SVG files from /assets/shapes/svg/
 * Measurements from Figma: 32px × 32px
 * 
 * Available shapes: 1, 2, 3, 4, 5, 6, 7
 * Can be used with random selection for dynamic suggestions
 */
export function SuggestionShapes({ 
  shape,
  className, 
  size = 32, 
  color,
  style = {},
  ...props
}: SuggestionShapeProps) {
  // If no shape is specified, randomly select one
  const selectedShape = shape || getRandomShape()
  
  const shapeStyle = {
    width: size,
    height: size,
    filter: color ? `brightness(0) saturate(100%) ${getColorFilter(color)}` : undefined,
    ...style,
  }

  return (
    <Image
      src={`/assets/shapes/svg/shape=${selectedShape}.svg`}
      alt={`Shape ${selectedShape}`}
      width={size}
      height={size}
      className={cn('flex-shrink-0', className)}
      style={shapeStyle}
      {...props}
    />
  )
}

/**
 * Get a random shape number (1-7)
 */
export function getRandomShape(): SuggestionShapeVariant {
  return (Math.floor(Math.random() * 7) + 1) as SuggestionShapeVariant
}

/**
 * Get multiple random shapes ensuring no duplicates
 */
export function getRandomShapes(count: number): SuggestionShapeVariant[] {
  const shapes: SuggestionShapeVariant[] = [1, 2, 3, 4, 5, 6, 7]
  const result: SuggestionShapeVariant[] = []
  
  for (let i = 0; i < Math.min(count, 7); i++) {
    const randomIndex = Math.floor(Math.random() * shapes.length)
    result.push(shapes.splice(randomIndex, 1)[0])
  }
  
  return result
}

// Helper function to convert colors to CSS filters
function getColorFilter(color: string): string {
  switch (color.toLowerCase()) {
    case 'white':
    case '#ffffff':
      return 'invert(100%)'
    case 'black':
    case '#000000':
      return 'invert(0%)'
    case '#2180ec': // Blue from design tokens
      return 'invert(27%) sepia(99%) saturate(1769%) hue-rotate(201deg) brightness(94%) contrast(91%)'
    case '#ff7d59': // Orange from design tokens
      return 'invert(59%) sepia(35%) saturate(4361%) hue-rotate(343deg) brightness(103%) contrast(101%)'
    case '#f7f7f7': // Neutral 10
      return 'invert(97%) sepia(3%) saturate(106%) hue-rotate(169deg) brightness(100%) contrast(93%)'
    case '#171717': // Neutral 50
      return 'invert(7%) sepia(6%) saturate(466%) hue-rotate(169deg) brightness(97%) contrast(89%)'
    default:
      return ''
  }
}

export default SuggestionShapes
