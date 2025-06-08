import React from 'react'

const ChatPreview = ({text}) => (
  <div
    style={{
      width: 270,
      height: 52,
      padding: 4,
      background: '#fff',
      display: 'flex',
      alignItems: 'center',
      fontFamily: 'Mabry Pro, sans-serif',
      fontWeight: 400,
      fontSize: 20,
      color: '#5A5A5A',
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      boxSizing: 'border-box',
    }}
  >
    {text}
  </div>
)

export default ChatPreview 