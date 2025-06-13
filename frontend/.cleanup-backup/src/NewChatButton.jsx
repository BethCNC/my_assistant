import React, {useState} from 'react'

const COLORS = {
  black: '#171717',
  blue: '#2180EC',
  white: '#FAFAFA',
}
const GRADIENT = 'linear-gradient(90deg, #69DEF2 0%, #126FD8 100%)'
const FOCUS_BORDER = '2px solid #fff'
const SHADOW = '0px 0px 1px 4px rgba(255,255,255,0.1), inset 0px 2px 1px 0px rgba(255,255,255,0.25), inset 0px -4px 2px 0px rgba(0,0,0,0.25)'
const NOISE_OVERLAY = '/assets/texture/noise.png'
const PLUS_ICON = '/assets/icons/plus.svg'

const NewChatButton = ({onClick, expanded = true}) => {
  const [state, setState] = useState('default')
  const [isFocused, setIsFocused] = useState(false)

  // Figma: bg #171717, hover/active #2180EC, text #FFF, border radius 8px, padding 0 16px, 48px height, 34px icon, 20px font
  let bg = COLORS.black
  let color = COLORS.white
  let border = 'none'
  let showNoise = false

  if (state === 'hover' || (isFocused && state !== 'active')) {
    bg = COLORS.blue
    color = COLORS.white
    showNoise = true
    if (isFocused) border = FOCUS_BORDER
  }
  if (state === 'active') {
    bg = GRADIENT
    color = COLORS.white
    showNoise = true
  }

  return (
    <button
      type='button'
      onClick={onClick}
      onMouseEnter={() => setState('hover')}
      onMouseLeave={() => setState('default')}
      onMouseDown={() => setState('active')}
      onMouseUp={() => setState('hover')}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: 182,
        height: 48,
        padding: '0 16px',
        borderRadius: 8,
        border,
        background: bg,
        outline: 'none',
        cursor: 'pointer',
        fontFamily: 'Mabry Pro, sans-serif',
        fontWeight: 700,
        fontSize: 20,
        color,
        lineHeight: 1.2,
        userSelect: 'none',
        overflow: 'hidden',
        transition: 'background 0.15s, color 0.15s, border 0.15s',
        gap: 16,
        boxShadow: 'none',
      }}
    >
      <span style={{zIndex: 1, fontWeight: 700, fontSize: 20, color}}>New Chat</span>
      <img src={PLUS_ICON} alt='plus' style={{width: 28, height: 28, marginLeft: 12, filter: 'brightness(0) invert(1)'}} />
      {showNoise && (
        <span
          style={{
            position: 'absolute',
            inset: 0,
            background: `url(${NOISE_OVERLAY}) center/cover`,
            opacity: 0.2,
            mixBlendMode: 'hard-light',
            pointerEvents: 'none',
            borderRadius: 8,
          }}
        />
      )}
    </button>
  )
}

export default NewChatButton 