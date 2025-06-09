import React, {useState} from 'react'

const COLORS = {
  black: '#171717',
  blue: '#2180EC',
  white: '#FAFAFA',
}
const GRADIENT = 'linear-gradient(90deg, #69DEF2 0%, #126FD8 100%)'
const FOCUS_BORDER = '2px solid #fff'
const SHADOW = '0px 0px 1px 4px rgba(255,255,255,0.1), inset 0px 2px 1px 0px rgba(255,255,255,0.25), inset 0px -4px 2px 0px rgba(0,0,0,0.25)'

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
        justifyContent: 'flex-start', // Figma: left-aligned
        gap: expanded ? 12 : 0,
        padding: expanded ? '0 16px' : 0, // Figma: 16px horizontal
        borderRadius: 8, // Figma: 8px
        border,
        background: bg,
        outline: 'none',
        cursor: 'pointer',
        fontFamily: 'Mabry Pro, sans-serif',
        fontWeight: 700,
        fontSize: expanded ? 20 : 0, // Figma: 20px
        color,
        lineHeight: 1.2,
        minWidth: 0,
        minHeight: 0,
        userSelect: 'none',
        overflow: 'hidden',
        transition: 'background 0.15s, color 0.15s, border 0.15s, font-size 0.2s, padding 0.2s',
        width: expanded ? 182 : 52,
        height: 48,
        boxShadow: 'none', // Remove shadow
      }}
    >
      <img src='/assets/plus.svg' alt='' style={{width: 34, height: 34, zIndex: 1, filter: color === COLORS.white ? 'invert(1)' : 'none', marginRight: expanded ? 12 : 0}} />
      {expanded && <span style={{zIndex: 1, fontWeight: 700, fontSize: 20, color}}>{'New Chat'}</span>}
      {showNoise && (
        <span
          style={{
            position: 'absolute',
            inset: 0,
            background: 'url(/assets/texture/noise.png) center/cover',
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