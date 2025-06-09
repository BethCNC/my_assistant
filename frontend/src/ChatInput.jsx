import React, {useState, useRef} from 'react'
import IconButton from './IconButton'

const COLORS = {
  border: '#171717',
  focus: '#2180EC',
  bg: '#fff',
  text: '#171717',
  subtext: '#5A5A5A',
  attachBar: '#fff',
  attachBorder: '#2180EC',
  sendBg: '#171717',
  sendBgActive: '#2180EC',
}
const MAX_LEN = 1000
const DEFAULT_THUMBS = [
  {type: 'image', name: 'thumbnail_image01.png', src: '/assets/thumbnails/thumbnail_image01.png'},
  {type: 'image', name: 'thumbnail_image02.png', src: '/assets/thumbnails/thumbnail_image02.png'},
  {type: 'image', name: 'thumbnail_image03.png', src: '/assets/thumbnails/thumbnail_image03.png'},
]

const ChatInput = ({value, onChange, onSend, attachments = [], onRemoveAttachment}) => {
  const [focus, setFocus] = useState(false)
  const [sendState, setSendState] = useState('default')
  const textareaRef = useRef(null)
  return (
    <div
      style={{
        width: '100%',
        background: COLORS.bg,
        borderRadius: 8,
        boxSizing: 'border-box',
        border: `2px solid ${focus ? COLORS.focus : COLORS.border}`,
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
        boxShadow: 'none',
      }}
    >
      {/* Attachments Bar */}
      {attachments && attachments.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: COLORS.attachBar,
            border: `2px solid ${COLORS.attachBorder}`,
            borderRadius: 8,
            padding: 8,
            marginBottom: 8,
          }}
        >
          {attachments.map((a, i) => (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 4}}>
              {a.type === 'image' ? (
                <img src={a.src} alt='' style={{width: 32, height: 32, borderRadius: 4, objectFit: 'cover'}} />
              ) : (
                <span style={{fontSize: 16, color: COLORS.text, fontFamily: 'Mabry Pro, sans-serif'}}>{a.name}</span>
              )}
              {a.progress != null && (
                <span style={{fontSize: 12, color: COLORS.subtext}}>{a.progress}%</span>
              )}
              {onRemoveAttachment && (
                <button onClick={() => onRemoveAttachment(i)} style={{background: 'none', border: 'none', color: COLORS.text, cursor: 'pointer', fontSize: 16, marginLeft: 2}}>×</button>
              )}
            </div>
          ))}
        </div>
      )}
      {/* Input Row */}
      <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
        {/* Left icon buttons */}
        <div style={{display: 'flex', flexDirection: 'row', gap: 8}}>
          <IconButton icon='icon-paperclip.svg' ariaLabel='Attach file' size={28} />
          <IconButton icon='icon-camera.svg' ariaLabel='Attach image' size={28} />
        </div>
        {/* Textarea */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 2, justifyContent: 'center'}}>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => onChange && onChange(e.target.value)}
            onFocus={() => setFocus(true)}
            onBlur={() => setFocus(false)}
            maxLength={MAX_LEN}
            placeholder='Ask me a question...'
            style={{
              width: '100%',
              minHeight: 40,
              maxHeight: 80,
              border: 'none',
              borderRadius: 8,
              fontFamily: 'Mabry Pro, sans-serif',
              fontWeight: 400,
              fontSize: 20,
              color: COLORS.text,
              padding: '10px 16px',
              resize: 'none',
              outline: 'none',
              boxSizing: 'border-box',
              background: COLORS.bg,
              display: 'flex',
              alignItems: 'center',
            }}
          />
          <div style={{display: 'flex', justifyContent: 'flex-end', color: COLORS.subtext, fontSize: 16, fontFamily: 'Mabry Pro, sans-serif'}}>
            {value?.length || 0}/{MAX_LEN}
          </div>
        </div>
        {/* Send button */}
        <button
          type='button'
          onClick={onSend}
          onMouseEnter={() => setSendState('hover')}
          onMouseLeave={() => setSendState('default')}
          onMouseDown={() => setSendState('active')}
          onMouseUp={() => setSendState('hover')}
          style={{
            width: 48,
            height: 48,
            borderRadius: 8,
            background: sendState === 'active' || sendState === 'hover' ? COLORS.sendBgActive : COLORS.sendBg,
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'background 0.15s',
            outline: 'none',
            padding: 0,
            marginLeft: 8,
          }}
        >
          <img src='/assets/icon-send.svg' alt='' style={{width: 24, height: 24, filter: 'invert(1)'}} />
        </button>
      </div>
    </div>
  )
}

export default ChatInput 