import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing, glassmorphism } from './tokens'

const Suggestion = ({ shape = 'asterisk', text, onClick, index = 0 }) => {
  const [isHovered, setIsHovered] = useState(false)
  
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        ...glassmorphism.light,
        border: 'none',
        borderRadius: radii.lg,
        padding: spacing.lg,
        color: colors.white,
        fontSize: fontSizes.base,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: spacing.md,
        transition: 'all 0.2s ease',
        textAlign: 'left',
        width: '100%',
        minHeight: 80,
        transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
        background: isHovered 
          ? 'rgba(255, 255, 255, 0.15)' 
          : 'rgba(255, 255, 255, 0.1)',
        boxShadow: isHovered
          ? '0 8px 32px rgba(0, 0, 0, 0.1)'
          : '0 4px 16px rgba(0, 0, 0, 0.05)',
      }}
    >
      <div style={{
        background: colors.black,
        borderRadius: radii.md,
        padding: spacing.sm,
        minWidth: 32,
        minHeight: 32,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <img 
          src={`/assets/${shape}.svg`} 
          alt="" 
          style={{
            width: 16,
            height: 16,
            filter: 'brightness(0) invert(1)', // Makes SVG white
          }}
        />
      </div>
      
      <span style={{ 
        flex: 1,
        fontWeight: 400,
        lineHeight: 1.4,
      }}>
        {text}
      </span>
      
      <span style={{ 
        fontSize: fontSizes.lg,
        opacity: 0.8,
        transition: 'transform 0.2s ease',
        transform: isHovered ? 'translateX(2px)' : 'translateX(0)',
      }}>
        →
      </span>
    </button>
  )
}

export default Suggestion