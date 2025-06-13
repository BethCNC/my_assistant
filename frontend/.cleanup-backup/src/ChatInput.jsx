import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing, glassmorphism } from './tokens'

const ChatInput = ({ value, onChange, onSend, disabled = false }) => {
  const [state, setState] = useState('default') // default, focus, filled
  const [isTyping, setIsTyping] = useState(false)

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  const handleFocus = () => {
    setState('focus')
  }

  const handleBlur = () => {
    setState(value && value.trim() ? 'filled' : 'default')
  }

  const handleChange = (e) => {
    const newValue = e.target.value
    onChange(e)
    setIsTyping(newValue.length > 0)
    setState(newValue.trim() ? 'filled' : 'focus')
  }

  const canSend = value && value.trim().length > 0 && !disabled

  // Define input states based on your Figma design system
  const getInputStyles = () => {
    const baseStyles = {
      borderRadius: radii.lg,
      padding: spacing.md,
      display: 'flex',
      alignItems: 'center',
      gap: spacing.md,
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    }

    const stateStyles = {
      default: {
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.05)',
      },
      focus: {
        background: 'rgba(255, 255, 255, 0.15)',
        backdropFilter: 'blur(20px)',
        border: '2px solid rgba(255, 255, 255, 0.4)',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(255, 255, 255, 0.1)',
        transform: 'translateY(-1px)',
      },
      filled: {
        background: 'rgba(255, 255, 255, 0.12)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)',
      }
    }

    return {
      ...baseStyles,
      ...stateStyles[state],
    }
  }

  const getButtonStyles = (type) => {
    const baseButtonStyles = {
      background: 'none',
      border: 'none',
      color: colors.white,
      cursor: 'pointer',
      padding: spacing.xs,
      borderRadius: radii.sm,
      transition: 'all 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }

    if (type === 'send') {
      return {
        background: canSend ? colors.black : 'rgba(0, 0, 0, 0.3)',
        color: canSend ? colors.white : 'rgba(255, 255, 255, 0.5)',
        border: 'none',
        borderRadius: radii.md,
        padding: spacing.sm,
        cursor: canSend ? 'pointer' : 'not-allowed',
        minWidth: 40,
        minHeight: 40,
        transition: 'all 0.2s ease',
        transform: canSend ? 'scale(1)' : 'scale(0.95)',
        opacity: canSend ? 1 : 0.6,
      }
    }

    return {
      ...baseButtonStyles,
      opacity: 0.8,
    }
  }

  return (
    <div style={getInputStyles()}>
      {/* Attachment button */}
      <button 
        style={getButtonStyles('attach')}
        onMouseEnter={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.1)'
          e.target.style.opacity = '1'
          e.target.style.transform = 'scale(1.1)'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'transparent'
          e.target.style.opacity = '0.8'
          e.target.style.transform = 'scale(1)'
        }}
      >
        <img 
          src='/assets/icon-paperclip.svg' 
          alt='Attach' 
          style={{
            width: 20,
            height: 20,
            filter: 'brightness(0) invert(1)',
          }}
        />
      </button>
      
      {/* Text input */}
      <input
        type="text"
        value={value || ''}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder="Ask me a question..."
        disabled={disabled}
        style={{
          flex: 1,
          background: 'none',
          border: 'none',
          color: colors.white,
          fontSize: fontSizes.base,
          outline: 'none',
          fontFamily: 'inherit',
          '::placeholder': {
            color: 'rgba(255, 255, 255, 0.6)',
          }
        }}
      />
      
      {/* Camera button */}
      <button 
        style={getButtonStyles('camera')}
        onMouseEnter={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.1)'
          e.target.style.opacity = '1'
          e.target.style.transform = 'scale(1.1)'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'transparent'
          e.target.style.opacity = '0.8'
          e.target.style.transform = 'scale(1)'
        }}
      >
        <img 
          src='/assets/icon-camera.svg' 
          alt='Camera' 
          style={{
            width: 20,
            height: 20,
            filter: 'brightness(0) invert(1)',
          }}
        />
      </button>

      {/* Character counter */}
      <div style={{
        color: state === 'focus' ? 'rgba(255, 255, 255, 0.8)' : 'rgba(255, 255, 255, 0.6)',
        fontSize: fontSizes.sm,
        minWidth: 'fit-content',
        transition: 'color 0.2s ease',
      }}>
        {(value || '').length}/1000
      </div>
      
      {/* Send button */}
      <button
        onClick={canSend ? onSend : undefined}
        disabled={!canSend}
        style={getButtonStyles('send')}
        onMouseEnter={(e) => {
          if (canSend) {
            e.target.style.transform = 'scale(1.05)'
            e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)'
          }
        }}
        onMouseLeave={(e) => {
          if (canSend) {
            e.target.style.transform = 'scale(1)'
            e.target.style.boxShadow = 'none'
          }
        }}
      >
        <img 
          src='/assets/icon-send.svg' 
          alt='Send' 
          style={{
            width: 20,
            height: 20,
            filter: 'brightness(0) invert(1)',
          }}
        />
      </button>
    </div>
  )
}

export default ChatInput