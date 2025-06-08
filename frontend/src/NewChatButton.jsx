import React, {useState} from 'react'

const COLORS = {
  black: '#171717',
  blue: '#2180EC',
  white: '#FAFAFA',
}
const GRADIENT = 'linear-gradient(90deg, #69DEF2 0%, #126FD8 100%)'
const FOCUS_BORDER = '2px solid #fff'
const SHADOW = '0px 0px 1px 4px rgba(255,255,255,0.1), inset 0px 2px 1px 0px rgba(255,255,255,0.25), inset 0px -4px 2px 0px rgba(0,0,0,0.25)'

const NewChatButton = ({onClick}) => {
  const [state, setState] = useState('default')
  const [isFocused, setIsFocused] = useState(false)

  let bg = COLORS.black
  let color = COLORS.white
  let border = 'none'
  let showNoise = false

  if (state === 'hover' || (isFocused && state !== 'active')) {
    bg = COLORS.blue
    color = COLORS.black
    showNoise = true
    if (isFocused) border = FOCUS_BORDER
  }
  if (state === 'active') {
    bg = GRADIENT
    color = COLORS.black
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
        gap: 12,
        padding: '12px 24px',
        borderRadius: 6,
        border,
        boxShadow: SHADOW,
        background: bg,
        outline: 'none',
        cursor: 'pointer',
        fontFamily: 'Mabry Pro, sans-serif',
        fontWeight: 700,
        fontSize: 28,
        color,
        lineHeight: 1.14,
        minWidth: 0,
        minHeight: 0,
        userSelect: 'none',
        overflow: 'hidden',
        transition: 'background 0.15s, color 0.15s, border 0.15s',
      }}
    >
      <img src='/assets/plus.svg' alt='' style={{width: 34, height: 34, zIndex: 1, filter: color === COLORS.white ? 'invert(1)' : 'none'}} />
      <span style={{zIndex: 1}}>{'New Chat'}</span>
      {showNoise && (
        <span
          style={{
            position: 'absolute',
            inset: 0,
            background: 'url(/assets/texture/noise.png) center/cover',
            opacity: 0.2,
            mixBlendMode: 'hard-light',
            pointerEvents: 'none',
            borderRadius: 6,
          }}
        />
      )}
    </button>
  )
}

export default NewChatButton 