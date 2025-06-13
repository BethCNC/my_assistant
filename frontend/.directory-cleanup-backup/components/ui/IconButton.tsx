import React from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { Icons, IconVariant } from './Icons'
import { ThumbnailImages, getRandomThumbnail } from './ThumbnailImages'

// Icon button variants from Figma documentation
export type IconButtonVariant = 'files' | 'images' | 'send'
export type IconButtonState = 'default' | 'hover' | 'active' | 'focus' | 'attached'

interface IconButtonProps {
  variant: IconButtonVariant
  state?: IconButtonState
  attachmentCount?: number
  onClick?: () => void
  disabled?: boolean
  className?: string
}

/**
 * Icon Buttons Component - Based on Figma design system
 * Uses actual SVG files from /assets/icons/
 * 
 * Measurements from Figma:
 * - Default: 44px × 44px
 * - With attachment count: 66px × 44px (files) or 100px × 44px (images)
 * 
 * Variants and Properties:
 * - variant: files, images, send
 * - state: default, hover, active, focus, attached
 * - Nested instances of Icons: 24px × 24px
 * - Attachment count text: Mabry Pro Bold 18px (files) or 12px (images)
 */
export function IconButton({ 
  variant, 
  state = 'default',
  attachmentCount,
  onClick,
  disabled = false,
  className 
}: IconButtonProps) {
  const hasAttachment = state === 'attached' && attachmentCount && attachmentCount > 0
  
  // Get icon based on variant - using actual icon names from assets
  const getIcon = (): IconVariant => {
    switch (variant) {
      case 'files':
        return 'files'  // maps to /assets/icons/files.svg
      case 'images':
        return 'images' // maps to /assets/icons/images.svg
      case 'send':
        return 'send'   // maps to /assets/icons/send.svg
      default:
        return 'files'
    }
  }

  // Get styles based on state from Figma documentation
  const getStateStyles = () => {
    switch (state) {
      case 'hover':
        return {
          backgroundColor: designTokens.colors.blue,
          color: designTokens.colors.white,
          iconColor: designTokens.colors.white,
        }
      case 'active':
        return {
          border: `1px solid ${designTokens.colors.blue}`,
          backgroundColor: 'transparent',
          color: designTokens.colors.neutral[10],
          iconColor: designTokens.colors.neutral[10],
        }
      case 'focus':
        return {
          backgroundColor: designTokens.colors.blue,
          color: designTokens.colors.white,
          iconColor: designTokens.colors.white,
          outline: `2px solid ${designTokens.colors.blue}`,
          outlineOffset: '2px',
        }
      case 'attached':
        return {
          border: `1px solid ${designTokens.colors.blue}`,
          backgroundColor: 'transparent',
          color: designTokens.colors.neutral[10],
          iconColor: designTokens.colors.neutral[10],
        }
      default:
        return {
          backgroundColor: 'transparent',
          color: designTokens.colors.black,
          iconColor: designTokens.colors.black,
        }
    }
  }

  // Get dimensions based on variant and attachment
  const getDimensions = () => {
    if (hasAttachment) {
      if (variant === 'images') {
        return { width: 100, height: 44 } // From Figma: 100px × 44px
      } else if (variant === 'files') {
        return { width: 66, height: 44 } // From Figma: 66px × 44px
      }
    }
    return { width: 44, height: 44 } // Default: 44px × 44px
  }

  const dimensions = getDimensions()
  const stateStyles = getStateStyles()

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        // Base styles
        'inline-flex items-center justify-center gap-1 rounded-lg transition-all',
        'hover:scale-105 active:scale-95',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      style={{
        width: dimensions.width,
        height: dimensions.height,
        padding: hasAttachment ? '10px' : '10px', // 10px padding from Figma
        backgroundColor: stateStyles.backgroundColor,
        color: stateStyles.color,
        border: stateStyles.border || 'none',
        outline: stateStyles.outline || 'none',
        outlineOffset: stateStyles.outlineOffset || '0',
      }}
    >
      {/* Icon using actual SVG files */}
      <Icons 
        icon={getIcon()} 
        size={24} 
        color={stateStyles.iconColor}
      />
      
      {/* Attachment count for files variant */}
      {hasAttachment && variant === 'files' && (
        <span
          className="font-primary font-bold leading-none"
          style={{
            fontSize: 18, // Mabry Pro Bold 18px from Figma
            color: designTokens.colors.neutral[10],
          }}
        >
          {attachmentCount}
        </span>
      )}
      
      {/* Thumbnail images for image attachments */}
      {hasAttachment && variant === 'images' && (
        <div className="flex items-center gap-1">
          <ThumbnailImages variant="01" size={22} />
          <ThumbnailImages variant="02" size={22} />
          {attachmentCount && attachmentCount > 2 && (
            <span
              className="font-primary font-bold leading-none ml-1"
              style={{
                fontSize: 12, // Mabry Pro Bold 12px from Figma
                color: designTokens.colors.neutral[10],
              }}
            >
              {attachmentCount > 2 ? `${attachmentCount - 2}+` : ''}
            </span>
          )}
        </div>
      )}
    </button>
  )
}

export default IconButton
