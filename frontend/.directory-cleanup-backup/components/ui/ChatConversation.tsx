import React from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'

interface ChatMessage {
  id: string
  sender: 'Assistant' | 'Beth' | string
  message: string
  timestamp: string
  isUser?: boolean
}

interface ChatConversationProps {
  messages?: ChatMessage[]
  className?: string
}

/**
 * Chat Conversation Component - Based on Figma design system
 * 
 * From Figma PDF documentation (page 18):
 * - Size: 950px × 560px
 * - Sender Name: Mabry Pro Bold 16px
 * - Time Sent: Mabry Pro Light 16px, color: #5C5C5C
 * - Message: Mabry Pro Medium 18px
 * - Container backgrounds: #F7F7F7 (light) and #0A0A0A (dark)
 * - Spacing: 48px, 16px, 32px, 12px from measurements
 * 
 * Structure:
 * - Alternating message bubbles
 * - Assistant messages: light background
 * - User messages: dark background
 * - Sender name and timestamp header
 * - Message content with proper spacing
 */
export function ChatConversation({ 
  messages = [],
  className 
}: ChatConversationProps) {
  
  // Default sample messages if none provided
  const defaultMessages: ChatMessage[] = [
    {
      id: '1',
      sender: 'Assistant',
      message: 'How can I help you today, Beth?',
      timestamp: '10 Min ago',
      isUser: false,
    },
    {
      id: '2',
      sender: 'Beth',
      message: 'I want to learn about UI design systems and how to build them in Figma.',
      timestamp: '12 Min ago',
      isUser: true,
    },
    {
      id: '3',
      sender: 'Assistant',
      message: 'Sure I can help you learn all about design systems in Figma. Where would you like to start?',
      timestamp: '10 Min ago',
      isUser: false,
    },
    {
      id: '4',
      sender: 'Beth',
      message: "Let's start by learning about figma variable collections and best practices for setting them up in terms of how many collections you should have and what types and what they should contain.",
      timestamp: '12 Min ago',
      isUser: true,
    },
  ]

  const displayMessages = messages.length > 0 ? messages : defaultMessages

  return (
    <div
      className={cn(
        'flex flex-col gap-4 overflow-y-auto p-4',
        className
      )}
      style={{
        width: 950, // 950px width from Figma
        height: 560, // 560px height from Figma
        padding: '16px', // Adjusted padding for better fit
      }}
    >
      {displayMessages.map((message, index) => (
        <div
          key={message.id || index}
          className={cn(
            'flex flex-col gap-2 max-w-[80%]',
            message.isUser ? 'ml-auto' : 'mr-auto'
          )}
        >
          {/* Message Header - Sender and Time */}
          <div 
            className="flex items-center gap-2"
            style={{
              marginBottom: '4px',
            }}
          >
            <span
              style={{
                fontSize: '16px', // Mabry Pro Bold 16px from Figma
                fontFamily: designTokens.fonts.primary,
                fontWeight: 700, // Bold
                color: '#0A0A0A', // Color from Figma
              }}
            >
              {message.sender}
            </span>
            <span
              style={{
                fontSize: '16px', // Mabry Pro Light 16px from Figma
                fontFamily: designTokens.fonts.primary,
                fontWeight: 300, // Light
                color: '#5C5C5C', // Color from Figma
              }}
            >
              {message.timestamp}
            </span>
          </div>

          {/* Message Bubble */}
          <div
            className={cn(
              'rounded-lg p-4 shadow-sm',
              'transition-all duration-200 hover:shadow-md'
            )}
            style={{
              backgroundColor: message.isUser 
                ? '#0A0A0A' // Dark background for user messages
                : '#F7F7F7', // Light background for assistant messages
              borderRadius: `${designTokens.radii.lg}px`,
              padding: '16px 20px', // Padding from Figma measurements
              maxWidth: '100%',
            }}
          >
            <p
              style={{
                fontSize: '18px', // Mabry Pro Medium 18px from Figma
                fontFamily: designTokens.fonts.primary,
                fontWeight: 500, // Medium
                color: message.isUser 
                  ? '#F7F7F7' // Light text for dark background
                  : '#0A0A0A', // Dark text for light background
                lineHeight: 1.5,
                margin: 0,
              }}
            >
              {message.message}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ChatConversation
