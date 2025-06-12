import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing, glassmorphism } from './tokens'

const ChatInput = ({ value, onChange, onSend, disabled = false }) => {
  const [isFocused, setIsFocused] = useState(false)

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  const canSend = value && value.trim().length > 0 && !disabled

  return (
    <div style={{
      ...glassmorphism.light,
      borderRadius: radii.lg,
      padding: spacing.md,
      display: 'flex',
      alignItems: 'center',
      gap: spacing.md,
      border: isFocused ? '1px solid rgba(255, 255, 255, 0.4)' : '1px solid rgba(255, 255, 255, 0.2)',
      transition: 'border 0.2s ease',
    }}>
      {/* Attachment button */}
      <button 
        style={{
          background: 'none',
          border: 'none',
          color: colors.white,
          fontSize: fontSizes.lg,
          cursor: 'pointer',
          padding: spacing.xs,
          borderRadius: radii.sm,
          transition: 'background 0.2s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: 0.8,
        }}
        onMouseEnter={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.1)'
          e.target.style.opacity = '1'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'transparent'
          e.target.style.opacity = '0.8'
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
        onChange={onChange}
        onKeyPress={handleKeyPress}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
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
        style={{
          background: 'none',
          border: 'none',
          color: colors.white,
          fontSize: fontSizes.lg,
          cursor: 'pointer',
          padding: spacing.xs,
          borderRadius: radii.sm,
          transition: 'background 0.2s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: 0.8,
        }}
        onMouseEnter={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.1)'
          e.target.style.opacity = '1'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'transparent'
          e.target.style.opacity = '0.8'
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
        color: 'rgba(255, 255, 255, 0.6)',
        fontSize: fontSizes.sm,
        minWidth: 'fit-content',
      }}>
        {(value || '').length}/1000
      </div>
      
      {/* Send button */}
      <button
        onClick={canSend ? onSend : undefined}
        disabled={!canSend}
        style={{
          background: canSend ? colors.black : 'rgba(0, 0, 0, 0.3)',
          color: canSend ? colors.white : 'rgba(255, 255, 255, 0.5)',
          border: 'none',
          borderRadius: radii.md,
          padding: spacing.sm,
          cursor: canSend ? 'pointer' : 'not-allowed',
          fontSize: fontSizes.lg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minWidth: 40,
          minHeight: 40,
          transition: 'all 0.2s ease',
          transform: canSend ? 'scale(1)' : 'scale(0.95)',
        }}
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