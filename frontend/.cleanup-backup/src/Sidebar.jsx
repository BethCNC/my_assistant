import React, { useState } from 'react'
import { colors, radii, fontSizes, spacing, glassmorphism } from './tokens'

const Sidebar = ({ chatList, onNewChat }) => {
  const [hoveredIndex, setHoveredIndex] = useState(null)
  const [newChatHovered, setNewChatHovered] = useState(false)

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
        transition: 'background 0.2s ease',
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
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.1)'
          e.target.style.transform = 'scale(1.1)'
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'transparent'
          e.target.style.transform = 'scale(1)'
        }}
        >
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
              opacity: hoveredIndex === index ? 1 : 0.8,
              background: hoveredIndex === index ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              transition: 'all 0.2s ease',
              transform: hoveredIndex === index ? 'translateX(4px)' : 'translateX(0)',
            }}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            {chat}
          </div>
        ))}
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        onMouseEnter={() => setNewChatHovered(true)}
        onMouseLeave={() => setNewChatHovered(false)}
        style={{
          background: newChatHovered ? '#2c2c2c' : colors.black,
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
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: newChatHovered 
            ? '0 8px 24px rgba(0, 0, 0, 0.3)' 
            : '0 4px 12px rgba(0, 0, 0, 0.2)',
          transform: newChatHovered ? 'translateY(-2px) scale(1.02)' : 'translateY(0) scale(1)',
        }}
      >
        New Chat
        <span style={{ 
          fontSize: fontSizes.lg,
          transition: 'transform 0.2s ease',
          transform: newChatHovered ? 'rotate(90deg)' : 'rotate(0deg)',
        }}>
          +
        </span>
      </button>
    </div>
  )
}

export default Sidebar