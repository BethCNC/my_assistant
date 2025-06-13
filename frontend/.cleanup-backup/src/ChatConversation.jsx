import React from 'react'

const AVATAR_USER = '/assets/smiley-white.svg'
const AVATAR_ASSISTANT = '/assets/shapes/svg/shape=5.svg'

const ChatConversation = ({messages = []}) => (
  <div style={{
    width: '100%',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
    padding: '24px 0',
    overflowY: 'auto',
    background: 'transparent',
  }}>
    {messages.map((msg, i) => {
      const isUser = msg.sender === 'user'
      return (
        <div key={msg.id || i} style={{
          display: 'flex',
          flexDirection: isUser ? 'row' : 'row-reverse',
          alignItems: 'flex-start',
          gap: 16,
          padding: '0 32px',
        }}>
          {/* Avatar */}
          <img
            src={isUser ? AVATAR_USER : AVATAR_ASSISTANT}
            alt='avatar'
            style={{width: 40, height: 40, borderRadius: '50%', marginTop: 0, background: isUser ? '#fff' : 'none', boxShadow: isUser ? '0 2px 8px 0 rgba(0,0,0,0.08)' : 'none'}}
          />
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-start' : 'flex-end'}}>
            {/* Meta */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              marginBottom: 4,
            }}>
              <span style={{fontFamily: 'Mabry Pro, sans-serif', fontWeight: 700, fontSize: 16, color: '#808080'}}>
                {isUser ? 'Beth' : 'Assistant'}
              </span>
              <span style={{fontFamily: 'Mabry Pro, sans-serif', fontWeight: 400, fontSize: 16, color: '#BFBFBF'}}>
                {msg.time}
              </span>
            </div>
            {/* Bubble */}
            <div style={{
              background: isUser ? '#171717' : '#fff',
              color: isUser ? '#fff' : '#171717',
              borderRadius: 18,
              boxShadow: '0 2px 8px 0 rgba(0,0,0,0.08)',
              fontFamily: 'Mabry Pro, sans-serif',
              fontWeight: 400,
              fontSize: 20,
              padding: '18px 28px',
              maxWidth: 700,
              textAlign: 'left',
              wordBreak: 'break-word',
            }}>
              {msg.text}
            </div>
          </div>
        </div>
      )
    })}
  </div>
)

export default ChatConversation 