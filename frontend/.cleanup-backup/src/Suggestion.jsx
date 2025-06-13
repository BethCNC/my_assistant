import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing, glassmorphism } from './tokens'

const Suggestion = ({ shape = 'asterisk', text, onClick, index = 0 }) => {
  const [state, setState] = useState('default') // default, hover, focus
  
  // Define suggestion card states based on your Figma design system
  const getCardStyles = () => {
    const baseStyles = {
      border: 'none',
      borderRadius: radii.lg,
      padding: spacing.lg,
      color: colors.white,
      fontSize: fontSizes.base,
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: spacing.md,
      textAlign: 'left',
      width: '100%',
      minHeight: 80,
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', // Smooth easing
      outline: 'none',
    }

    const stateStyles = {
      default: {
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        transform: 'translateY(0px)',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.05)',
      },
      hover: {
        background: 'rgba(255, 255, 255, 0.15)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        transform: 'translateY(-4px)', // Lift effect
        boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15)', // Elevated shadow
      },
      focus: {
        background: 'rgba(255, 255, 255, 0.12)',
        backdropFilter: 'blur(20px)',
        border: '2px solid rgba(255, 255, 255, 0.5)', // Focus ring
        transform: 'translateY(-2px)',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(255, 255, 255, 0.2)', // Focus glow
      }
    }

    return {
      ...baseStyles,
      ...stateStyles[state],
    }
  }

  const getIconStyles = () => ({
    background: colors.black,
    borderRadius: radii.md,
    padding: spacing.sm,
    minWidth: 32,
    minHeight: 32,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'transform 0.2s ease',
    transform: state === 'hover' ? 'scale(1.1)' : 'scale(1)', // Icon scale on hover
  })

  const getArrowStyles = () => ({
    fontSize: fontSizes.lg,
    opacity: state === 'hover' ? 1 : 0.8,
    transition: 'all 0.2s ease',
    transform: state === 'hover' ? 'translateX(4px)' : 'translateX(0)', // Arrow slide
  })
  
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setState('hover')}
      onMouseLeave={() => setState('default')}
      onFocus={() => setState('focus')}
      onBlur={() => setState('default')}
      style={getCardStyles()}
    >
      <div style={getIconStyles()}>
        <img 
          src={`/assets/${shape}.svg`} 
          alt="" 
          style={{
            width: 16,
            height: 16,
            filter: 'brightness(0) invert(1)',
            transition: 'transform 0.2s ease',
          }}
        />
      </div>
      
      <span style={{ 
        flex: 1,
        fontWeight: 400,
        lineHeight: 1.4,
        transition: 'color 0.2s ease',
      }}>
        {text}
      </span>
      
      <span style={getArrowStyles()}>
        →
      </span>
    </button>
  )
}

export default Suggestion