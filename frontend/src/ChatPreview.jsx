import React, {useState} from 'react'

// Figma: 270x52px, 8px border radius, #737373 text, 16px font, ellipsis, hover bg rgba(115,115,115,0.08), no border, left-aligned, Mabry Pro
const ChatPreview = ({text}) => {
  const [hover, setHover] = useState(false)
  return (
    <div
      style={{
        width: 270,
        height: 52,
        padding: 4,
        background: hover ? 'rgba(115,115,115,0.08)' : 'transparent',
        display: 'flex',
        alignItems: 'center',
        fontFamily: 'Mabry Pro, sans-serif',
        fontWeight: 400,
        fontSize: 16,
        color: '#737373',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        boxSizing: 'border-box',
        borderRadius: 8,
        transition: 'background 0.15s',
        cursor: 'pointer',
        justifyContent: 'flex-start',
      }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {text}
    </div>
  )
}

export default ChatPreview 