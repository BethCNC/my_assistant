import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { Icons, IconVariant } from './Icons'
import { ThumbnailImages } from './ThumbnailImages'

// Icon button variants from Figma documentation
export type IconButtonState = 'default' | 'hover' | 'active' | 'focus' | 'attached'

interface IconButtonProps {
  icon: IconVariant
  state?: IconButtonState
  onClick?: () => void
  disabled?: boolean
  className?: string
  count?: string | null
  thumbnails?: string[]
}

/**
 * Icon Button Component - Updated to match exact Figma specifications
 * 
 * Key improvements:
 * - Support for attachment thumbnails
 * - Proper count display for files
 * - Dynamic sizing based on content
 * - Exact measurements from Figma PDFs
 */
export function IconButton({ 
  icon,
  state = 'default',
  onClick,
  disabled = false,
  className,
  count = null,
  thumbnails = [],
  ...props
}: IconButtonProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  const getButtonStyle = () => {
    const baseStyle = {
      width: count ? (thumbnails.length > 0 ? '100px' : '66px') : '44px',
      height: '44px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: '8px',
      border: 'none',
      cursor: disabled ? 'not-allowed' : 'pointer',
      position: 'relative' as const,
      padding: count ? '10px' : '10px',
      gap: thumbnails.length > 0 ? '5px' : '2px'
    }

    // Handle different states
    if (state === "focus" || isFocused) {
      return {
        ...baseStyle,
        backgroundColor: 'transparent',
        border: '2px solid #2180EC'
      }
    }
    
    if (state === "hover" || isHovered) {
      return {
        ...baseStyle,
        backgroundColor: 'transparent'
      }
    }
    
    if (state === "active") {
      return {
        ...baseStyle,
        backgroundColor: 'transparent',
        border: '1px solid #2180EC'
      }
    }

    if (state === "attached" && count) {
      return {
        ...baseStyle,
        backgroundColor: 'transparent',
        border: '1px solid #2180EC'
      }
    }

    return {
      ...baseStyle,
      backgroundColor: 'transparent'
    }
  }

  const getIconColor = () => {
    if (state === "hover" || isHovered || state === "focus" || isFocused) {
      return '#2180EC'
    }
    return '#000000'
  }

  return (
    <button
      style={getButtonStyle()}
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      className={className}
      {...props}
    >
      {/* Show thumbnails for image attachments */}
      {thumbnails.length > 0 && (
        <div className="flex items-center space-x-1">
          {thumbnails.slice(0, 2).map((variant, index) => (
            <ThumbnailImages 
              key={index}
              variant={variant as '01' | '02' | '03' | '04'} 
              size={21} 
            />
          ))}
        </div>
      )}
      
      {/* Show count for attachments */}
      {count && !thumbnails.length && (
        <span 
          style={{
            fontFamily: 'Mabry Pro',
            fontWeight: '700',
            fontSize: '18px',
            color: '#F7F7F7',
            marginRight: '2px'
          }}
        >
          {count}
        </span>
      )}
      
      {/* Show icon */}
      <div style={{ color: getIconColor() }}>
        <Icons icon={icon} />
      </div>
      
      {/* Show additional count for thumbnails */}
      {thumbnails.length > 2 && (
        <span 
          style={{
            fontFamily: 'Mabry Pro',
            fontWeight: '700',
            fontSize: '12px',
            color: '#F7F7F7',
            marginLeft: '4px'
          }}
        >
          +{thumbnails.length - 2}
        </span>
      )}
    </button>
  )
}

export default IconButton