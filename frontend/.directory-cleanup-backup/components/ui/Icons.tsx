import React from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

// Icon variant types from your assets/icons folder
export type IconVariant = 
  | 'arrow'
  | 'files' 
  | 'images'
  | 'minus'
  | 'plus'
  | 'send'
  | 'trash'

interface IconProps {
  icon: IconVariant
  className?: string
  size?: number
  color?: string
  style?: React.CSSProperties
}

/**
 * Icons Component - Based on Figma design system
 * Uses actual SVG files from /assets/icons/
 * Measurements from Figma: 24px × 24px (default)
 * 
 * Available icons: arrow, files, images, minus, plus, send, trash
 */
export function Icons({ 
  icon, 
  className, 
  size = 24, 
  color,
  style = {},
  ...props
}: IconProps) {
  const iconStyle = {
    width: size,
    height: size,
    filter: color ? `brightness(0) saturate(100%) ${getColorFilter(color)}` : undefined,
    ...style,
  }

  return (
    <Image
      src={`/assets/icons/${icon}.svg`}
      alt={`${icon} icon`}
      width={size}
      height={size}
      className={cn('flex-shrink-0', className)}
      style={iconStyle}
      {...props}
    />
  )
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

export default Icons
