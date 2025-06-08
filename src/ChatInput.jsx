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
}
const MAX_LEN = 1000
const DEFAULT_THUMBS = [
  {type: 'image', name: 'thumbnail_image01.png', src: '/assets/thumbnails/thumbnail_image01.png'},
  {type: 'image', name: 'thumbnail_image02.png', src: '/assets/thumbnails/thumbnail_image02.png'},
  {type: 'image', name: 'thumbnail_image03.png', src: '/assets/thumbnails/thumbnail_image03.png'},
]

const ChatInput = ({value, onChange, onSend, attachments = DEFAULT_THUMBS, onRemoveAttachment}) => {
  const [focus, setFocus] = useState(false)
  const textareaRef = useRef(null)
  return (
    <div
      style={{
        width: '100%',
        background: COLORS.bg,
        borderRadius: 12,
        padding: '16px 20px',
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
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
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 8}}>
        {/* Left icon buttons */}
        <div style={{display: 'flex', flexDirection: 'column', gap: 8}}>
          <IconButton icon='icon-paperclip.svg' ariaLabel='Attach file' />
          <IconButton icon='icon-camera.svg' ariaLabel='Attach image' />
        </div>
        {/* Textarea */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 4}}>
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
              minHeight: 64,
              border: `2px solid ${focus ? COLORS.focus : COLORS.border}`,
              borderRadius: 8,
              fontFamily: 'Mabry Pro, sans-serif',
              fontWeight: 400,
              fontSize: 20,
              color: COLORS.text,
              padding: 12,
              resize: 'vertical',
              outline: 'none',
              boxSizing: 'border-box',
              background: COLORS.bg,
              transition: 'border 0.15s',
            }}
          />
          <div style={{display: 'flex', justifyContent: 'flex-end', color: COLORS.subtext, fontSize: 16, fontFamily: 'Mabry Pro, sans-serif'}}>
            {value?.length || 0}/{MAX_LEN}
          </div>
        </div>
        {/* Send button */}
        <div style={{alignSelf: 'flex-end'}}>
          <IconButton icon='icon-send.svg' ariaLabel='Send' />
        </div>
      </div>
    </div>
  )
}

export default ChatInput 