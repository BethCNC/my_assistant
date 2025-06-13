import React from 'react'
import { cn } from '@/lib/utils'

// Thumbnail variants from Figma documentation (PDF page 13)
export type ThumbnailVariant = '01' | '02' | '03' | '04'

interface ThumbnailImagesProps {
  variant?: ThumbnailVariant
  size?: number
  className?: string
  onClick?: () => void
}

/**
 * Thumbnail Images Component - Based on Figma design system
 * 
 * From Figma PDF documentation:
 * - Size: 21px × 21px (can be scaled)
 * - 4 variants: 01, 02, 03, 04
 * - Used as placeholder images in attachment buttons
 * 
 * These are colorful geometric patterns used in:
 * - Icon buttons with attachments
 * - Chat input attachment previews
 * - File preview thumbnails
 * 
 * Since these are placeholders, they use CSS gradients instead of actual image files
 */
export function ThumbnailImages({ 
  variant = '01',
  size = 21,
  className,
  onClick 
}: ThumbnailImagesProps) {
  
  // Get the appropriate gradient based on variant
  const getImageStyles = () => {
    switch (variant) {
      case '01':
        return {
          background: 'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%)',
          borderRadius: '4px',
        }
      case '02':
        return {
          background: 'linear-gradient(135deg, #feca57 0%, #ff9ff3 50%, #54a0ff 100%)',
          borderRadius: '4px',
        }
      case '03':
        return {
          background: 'linear-gradient(135deg, #5f27cd 0%, #00d2d3 50%, #ff9ff3 100%)',
          borderRadius: '4px',
        }
      case '04':
        return {
          background: 'linear-gradient(135deg, #ff6348 0%, #2ed573 50%, #3742fa 100%)',
          borderRadius: '4px',
        }
      default:
        return {
          background: 'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%)',
          borderRadius: '4px',
        }
    }
  }

  const imageStyles = getImageStyles()

  return (
    <div
      onClick={onClick}
      className={cn(
        'flex-shrink-0 relative overflow-hidden transition-all duration-200',
        onClick && 'cursor-pointer hover:scale-110',
        className
      )}
      style={{
        width: size,
        height: size,
        ...imageStyles,
      }}
    >
      {/* Add subtle pattern overlay for more visual interest */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          background: `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.5) 0%, transparent 50%)`,
        }}
      />
      
      {/* Add small geometric shape for each variant */}
      <div className="absolute inset-0 flex items-center justify-center">
        {variant === '01' && (
          <div 
            className="w-2 h-2 bg-white/40 rounded-full"
            style={{ transform: 'translate(-2px, -2px)' }}
          />
        )}
        {variant === '02' && (
          <div 
            className="w-2 h-2 bg-white/40"
            style={{ 
              transform: 'translate(2px, -2px) rotate(45deg)',
              borderRadius: '1px',
            }}
          />
        )}
        {variant === '03' && (
          <div 
            className="w-2 h-2 bg-white/40"
            style={{ 
              transform: 'translate(-2px, 2px)',
              clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)',
            }}
          />
        )}
        {variant === '04' && (
          <div 
            className="w-2 h-2 bg-white/40 rounded-full"
            style={{ transform: 'translate(2px, 2px)' }}
          />
        )}
      </div>
    </div>
  )
}

// Helper function to get random thumbnail variant
export const getRandomThumbnail = (): ThumbnailVariant => {
  const variants: ThumbnailVariant[] = ['01', '02', '03', '04']
  return variants[Math.floor(Math.random() * variants.length)]
}

export default ThumbnailImages