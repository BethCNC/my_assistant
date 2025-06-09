import React, {useState} from 'react'

// Figma: 270x52px, 6px radius, #737373 text, 16px font, ellipsis, hover bg rgba(115,115,115,0.08), no border, left-aligned, Mabry Pro
const ChatPreview = ({text, expanded = true}) => {
  const [hover, setHover] = useState(false)
  return (
    <div
      style={{
        width: expanded ? 270 : 52,
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
        borderRadius: 6,
        transition: 'background 0.15s, width 0.2s',
        cursor: 'pointer',
        justifyContent: expanded ? 'flex-start' : 'center',
      }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {expanded ? text : <img src='/assets/icons/arrow.svg' alt='' style={{width: 24, height: 24, opacity: 0.5}} />}
    </div>
  )
}

export default ChatPreview 