import React, {useState} from 'react'
import NewChatButton from './NewChatButton'
import ChatPreview from './ChatPreview'

const Sidebar = ({chatList = [], onNewChat}) => {
  const [expanded, setExpanded] = useState(true)
  return (
    <aside
      style={{
        width: expanded ? 300 : 80,
        height: '100vh',
        background: 'radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.36) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: 12,
        border: 'none',
        boxShadow: '0px 2px 2px -1px rgba(0,0,0,0.16), 0px 2px 4px -2px rgba(0,0,0,0.16)',
        backdropFilter: 'blur(32px)',
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: 0,
        transition: 'width 0.2s',
        boxSizing: 'border-box',
        alignItems: 'stretch',
      }}
    >
      {/* Header */}
      <div style={{height: 64, borderTopLeftRadius: 12, borderTopRightRadius: 12, background: '#171717', display: 'flex', alignItems: 'center', justifyContent: expanded ? 'space-between' : 'center', padding: expanded ? '0 24px' : 0}}>
        {expanded && (
          <span style={{fontFamily: 'Mabry Pro, sans-serif', fontWeight: 700, fontSize: 28, color: '#fff'}}>Recents Chat</span>
        )}
        <button
          onClick={() => setExpanded(e => !e)}
          style={{
            width: 40,
            height: 40,
            borderRadius: 8,
            background: 'none',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)',
            transition: 'transform 0.2s',
          }}
        >
          <img src='/assets/icon-arrow.svg' alt='' style={{width: 32, height: 32, filter: 'invert(1)'}} />
        </button>
      </div>
      {/* Chat List */}
      <div style={{flex: 1, width: '100%', display: 'flex', flexDirection: 'column', gap: 0, padding: expanded ? '12px 0' : '12px 0', alignItems: 'center', overflowY: 'auto'}}>
        {chatList.map((text, i) => (
          <ChatPreview key={i} text={text} expanded={expanded} />
        ))}
      </div>
      {/* New Chat Button */}
      <div style={{width: '100%', height: 64, background: '#171717', borderBottomLeftRadius: 12, borderBottomRightRadius: 12, display: 'flex', alignItems: 'center', justifyContent: expanded ? 'flex-start' : 'center', padding: expanded ? '0 24px' : 0}}>
        <NewChatButton expanded={expanded} onClick={onNewChat} />
      </div>
    </aside>
  )
}

export default Sidebar 