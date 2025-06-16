import React from 'react'
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
  | 'paperclip'
  | 'camera'

interface IconProps {
  icon: IconVariant
  className?: string
  size?: number
  color?: string
  style?: React.CSSProperties
}

/**
 * Icons Component - Fixed file paths for assets
 * Uses actual SVG files from /assets/icons/
 * Measurements from Figma: 24px × 24px (default)
 */
export function Icons({ 
  icon, 
  className, 
  size = 24, 
  color = '#000000',
  style = {},
  ...props
}: IconProps) {
  // Map icon names to actual file names
  const iconFileMap: Record<IconVariant, string> = {
    arrow: 'arrow',
    files: 'files', 
    images: 'images',
    minus: 'minus',
    plus: 'plus',
    send: 'send',
    trash: 'trash',
    paperclip: 'files', // Use files icon for paperclip
    camera: 'images', // Use images icon for camera
  }

  const iconStyle = {
    width: size,
    height: size,
    filter: getColorFilter(color),
    ...style,
  }

  return (
    <img
      src={`/assets/icons/${iconFileMap[icon]}.svg`}
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
    case '#fff':
      return 'brightness(0) invert(1)'
    case 'black':
    case '#000000':
    case '#000':
      return 'brightness(0) invert(0)'
    case '#2180ec': // Blue from design tokens
      return 'brightness(0) saturate(100%) invert(27%) sepia(99%) saturate(1769%) hue-rotate(201deg) brightness(94%) contrast(91%)'
    case '#ff7d59': // Orange from design tokens
      return 'brightness(0) saturate(100%) invert(59%) sepia(35%) saturate(4361%) hue-rotate(343deg) brightness(103%) contrast(101%)'
    case '#f7f7f7': // Neutral 10
      return 'brightness(0) saturate(100%) invert(97%) sepia(3%) saturate(106%) hue-rotate(169deg) brightness(100%) contrast(93%)'
    case '#171717': // Neutral 50
      return 'brightness(0) saturate(100%) invert(7%) sepia(6%) saturate(466%) hue-rotate(169deg) brightness(97%) contrast(89%)'
    default:
      return 'brightness(0) invert(0)'
  }
}

export default Icons