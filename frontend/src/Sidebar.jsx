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
        borderRadius: 4,
        border: '2px solid',
        borderImage: 'linear-gradient(180deg, rgba(255,255,255,0.3), rgba(255,255,255,0.7)) 1',
        boxShadow: '0px 2px 2px -1px rgba(0,0,0,0.16), 0px 2px 4px -2px rgba(0,0,0,0.16)',
        backdropFilter: 'blur(32px)',
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 24,
        transition: 'width 0.2s',
        boxSizing: 'border-box',
        alignItems: expanded ? 'flex-start' : 'center',
      }}
    >
      {/* Header */}
      <div style={{display: 'flex', alignItems: 'center', width: '100%', justifyContent: expanded ? 'space-between' : 'center'}}>
        {expanded && (
          <span style={{fontFamily: 'Mabry Pro, sans-serif', fontWeight: 700, fontSize: 20, color: '#171717'}}>Recent Chats</span>
        )}
        <button
          onClick={() => setExpanded(e => !e)}
          style={{
            width: 40,
            height: 40,
            borderRadius: 8,
            background: '#171717',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            marginLeft: expanded ? 0 : 0,
            transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)',
            transition: 'transform 0.2s',
          }}
        >
          <img src='/assets/icon-arrow.svg' alt='' style={{width: 24, height: 24, filter: 'invert(1)'}} />
        </button>
      </div>
      {/* New Chat Button */}
      <div style={{width: '100%', display: 'flex', justifyContent: expanded ? 'flex-start' : 'center'}}>
        <NewChatButton onClick={onNewChat} />
      </div>
      {/* Chat List */}
      <div style={{width: '100%', display: 'flex', flexDirection: 'column', gap: 12}}>
        {chatList.map((text, i) => (
          <ChatPreview key={i} text={text} />
        ))}
      </div>
    </aside>
  )
}

export default Sidebar 