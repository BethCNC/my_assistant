import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing } from './tokens'

const ToolButton = ({ icon, label, active = false, onClick }) => {
  const [state, setState] = useState('default') // default, hover, focus, active
  
  // Define states based on your Figma design system
  const getButtonStyles = () => {
    const baseStyles = {
      display: 'flex',
      alignItems: 'center',
      gap: spacing.sm,
      borderRadius: radii.lg,
      padding: `${spacing.sm}px ${spacing.lg}px`,
      fontSize: fontSizes.base,
      fontWeight: 500,
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      minWidth: 100,
      border: 'none',
      outline: 'none',
    }

    if (active) {
      // Active button (like "Notion" selected)
      return {
        ...baseStyles,
        background: colors.white,
        color: colors.black,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        transform: state === 'hover' ? 'scale(1.02)' : 'scale(1)',
      }
    } else {
      // Inactive buttons
      const stateStyles = {
        default: {
          background: colors.black,
          color: colors.white,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          transform: 'scale(1)',
        },
        hover: {
          background: '#2c2c2c', // Slightly lighter black
          color: colors.white,
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
          transform: 'scale(1.02)',
        },
        focus: {
          background: colors.black,
          color: colors.white,
          boxShadow: '0 0 0 2px rgba(255, 255, 255, 0.5)',
          transform: 'scale(1)',
        },
        active: {
          background: '#1a1a1a', // Darker black
          color: colors.white,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
          transform: 'scale(0.98)',
        }
      }
      
      return {
        ...baseStyles,
        ...stateStyles[state],
      }
    }
  }
  
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setState('hover')}
      onMouseLeave={() => setState('default')}
      onMouseDown={() => setState('active')}
      onMouseUp={() => setState('hover')}
      onFocus={() => setState('focus')}
      onBlur={() => setState('default')}
      style={getButtonStyles()}
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