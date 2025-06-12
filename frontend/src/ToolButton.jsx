import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing } from './tokens'

const ToolButton = ({ icon, label, active = false, onClick }) => {
  const [isHovered, setIsHovered] = useState(false)
  
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        background: active ? colors.white : colors.black,
        color: active ? colors.black : colors.white,
        border: 'none',
        borderRadius: radii.lg,
        padding: `${spacing.sm}px ${spacing.lg}px`,
        fontSize: fontSizes.base,
        fontWeight: 500,
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        minWidth: 100,
        display: 'flex',
        alignItems: 'center',
        gap: spacing.sm,
        transform: isHovered ? 'scale(1.02)' : 'scale(1)',
        boxShadow: active 
          ? '0 4px 12px rgba(0, 0, 0, 0.15)' 
          : '0 2px 8px rgba(0, 0, 0, 0.1)',
      }}
    >
      {icon && (
        <img 
          src={`/assets/${icon}`} 
          alt="" 
          style={{
            width: 16,
            height: 16,
            filter: active ? 'none' : 'brightness(0) invert(1)',
          }}
        />
      )}
      {label}
    </button>
  )
}

export default ToolButton