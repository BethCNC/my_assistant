import React, {useState} from 'react'

const COLORS = {
  default: '#2180EC',
  hover: '#42A5F5',
  active: '#1565C0',
  focusBorder: '#019CFE',
}

const IconButton = ({icon, ariaLabel = ''}) => {
  const [state, setState] = useState('default')
  const [isFocused, setIsFocused] = useState(false)

  let bg = COLORS.default
  let border = 'none'
  if (state === 'hover') bg = COLORS.hover
  if (state === 'active') bg = COLORS.active
  if (isFocused) border = `2px solid ${COLORS.focusBorder}`

  return (
    <button
      aria-label={ariaLabel}
      style={{
        position: 'relative',
        width: 40,
        height: 40,
        borderRadius: 8,
        background: bg,
        border,
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 0,
        outline: 'none',
        cursor: 'pointer',
        transition: 'background 0.15s, border 0.15s',
      }}
      onMouseEnter={() => setState('hover')}
      onMouseLeave={() => setState('default')}
      onMouseDown={() => setState('active')}
      onMouseUp={() => setState('hover')}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      tabIndex={0}
    >
      <img
        src={`/assets/${icon}`}
        alt=""
        style={{width: 24, height: 24, zIndex: 1, position: 'relative', filter: 'brightness(0) invert(1)'}}
      />
      <span
        style={{
          position: 'absolute',
          inset: 0,
          background: 'url(/assets/texture/noise.png) center/cover',
          opacity: 0.2,
          mixBlendMode: 'hard-light',
          pointerEvents: 'none',
          zIndex: 2,
        }}
      />
    </button>
  )
}

export default IconButton 