import React, {useState} from 'react'

const SHAPES = [
  'shapes/svg/shape=1.svg',
  'shapes/svg/shape=2.svg',
  'shapes/svg/shape=3.svg',
  'shapes/svg/shape=4.svg',
  'shapes/svg/shape=5.svg',
  'shapes/svg/shape=6.svg',
  'shapes/svg/shape=7.svg',
]

const COLORS = {
  border: '#171717',
  bg: '#fff',
  hoverBorder: '#FFB36A',
  hoverBg: '#FFF4E7',
  focusBorder: '#2180EC',
  focusBg: '#EAF6FF',
  text: '#171717',
  iconBg: '#171717',
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

const Suggestion = ({text, onClick}) => {
  const [state, setState] = useState('default')
  // Pick a random shape and rotation for each card instance
  const [shape] = useState(() => SHAPES[getRandomInt(0, SHAPES.length - 1)])
  const [rotation] = useState(() => getRandomInt(-30, 30))

  let border = COLORS.border
  let bg = COLORS.bg
  if (state === 'hover') {
    border = COLORS.hoverBorder
    bg = COLORS.hoverBg
  }
  if (state === 'focus') {
    border = COLORS.focusBorder
    bg = COLORS.focusBg
  }
  return (
    <button
      type='button'
      onClick={onClick}
      onMouseEnter={() => setState('hover')}
      onMouseLeave={() => setState('default')}
      onFocus={() => setState('focus')}
      onBlur={() => setState('default')}
      style={{
        display: 'flex',
        alignItems: 'center',
        width: 600,
        minHeight: 64,
        borderRadius: 5,
        border: `2px solid ${border}`,
        background: bg,
        padding: 20,
        gap: 16,
        cursor: 'pointer',
        transition: 'border 0.15s, background 0.15s',
        overflow: 'hidden',
      }}
    >
      <span style={{
        width: 56,
        height: 56,
        borderRadius: 8,
        background: COLORS.iconBg,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        <img src={`/assets/${shape}`} alt='' style={{width: 32, height: 32, transform: `rotate(${rotation}deg)`}} />
      </span>
      <span style={{
        flex: 1,
        fontFamily: 'Mabry Pro, sans-serif',
        fontWeight: 700,
        fontSize: 20,
        color: COLORS.text,
        marginLeft: 24,
        marginRight: 24,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        textAlign: 'left',
      }}>{text}</span>
      <span style={{
        width: 40,
        height: 40,
        borderRadius: 8,
        background: '#fff',
        border: `2px solid ${COLORS.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 0,
        flexShrink: 0,
      }}>
        <img src='/assets/icon-arrow.svg' alt='' style={{width: 24, height: 24}} />
      </span>
    </button>
  )
}

export default Suggestion 