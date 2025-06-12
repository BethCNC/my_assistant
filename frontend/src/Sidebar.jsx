import React from 'react'
import { colors, radii, fontSizes, spacing, glassmorphism } from './tokens'

const Sidebar = ({ chatList, onNewChat }) => {
  return (
    <div style={{
      width: 280,
      ...glassmorphism.dark,
      display: 'flex',
      flexDirection: 'column',
      padding: spacing.lg,
      gap: spacing.md,
      height: '100vh',
    }}>
      {/* Sidebar header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: spacing.md,
        padding: spacing.md,
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: radii.lg,
        marginBottom: spacing.lg,
      }}>
        <img 
          src='/assets/smiley.svg' 
          alt='' 
          style={{
            width: 20,
            height: 20,
            filter: 'brightness(0) invert(1)',
          }}
        />
        <span style={{
          color: colors.white,
          fontWeight: 500,
          fontSize: fontSizes.base,
        }}>
          Recent Chat
        </span>
        <button style={{
          marginLeft: 'auto',
          background: 'none',
          border: 'none',
          color: colors.white,
          cursor: 'pointer',
          fontSize: fontSizes.lg,
          padding: spacing.xs,
          borderRadius: radii.sm,
          transition: 'background 0.2s ease',
        }}>
          ←
        </button>
      </div>

      {/* Chat list */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: spacing.xs,
        overflow: 'auto',
      }}>
        {chatList.map((chat, index) => (
          <div 
            key={index} 
            style={{
              color: colors.white,
              fontSize: fontSizes.sm,
              padding: spacing.sm,
              borderRadius: radii.sm,
              cursor: 'pointer',
              opacity: 0.8,
              transition: 'all 0.2s ease',
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
            {chat}
          </div>
        ))}
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        style={{
          background: colors.black,
          color: colors.white,
          border: 'none',
          borderRadius: radii.lg,
          padding: `${spacing.md}px ${spacing.lg}px`,
          fontSize: fontSizes.base,
          fontWeight: 500,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: spacing.sm,
          transition: 'all 0.2s ease',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = 'scale(1.02)'
          e.target.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.3)'
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = 'scale(1)'
          e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)'
        }}
      >
        New Chat
        <span style={{ fontSize: fontSizes.lg }}>+</span>
      </button>
    </div>
  )
}

export default Sidebar