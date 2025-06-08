import React, {useState} from 'react'
import Shape from './SuggestionShapes'
import IconSet from './IconSet'

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

const Suggestion = ({shape, text, onClick}) => {
  const [state, setState] = useState('default')
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
        <Shape shape={shape} />
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
        <IconSet icon='icon-arrow.svg' />
      </span>
    </button>
  )
}

export default Suggestion 