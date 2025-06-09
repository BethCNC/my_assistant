import React, {useState} from 'react'
import NewChatButton from './NewChatButton'
import ChatPreview from './ChatPreview'

const Sidebar = ({chatList = [], onNewChat}) => {
  return (
    <aside
      style={{
        width: 300,
        height: '100vh',
        background: '#171717',
        borderTopLeftRadius: 8,
        borderBottomLeftRadius: 8,
        borderTopRightRadius: 0,
        borderBottomRightRadius: 0,
        border: 'none',
        boxShadow: 'none',
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: 0,
        boxSizing: 'border-box',
        alignItems: 'stretch',
      }}
    >
      {/* Header */}
      <div style={{height: 64, borderTopLeftRadius: 8, background: '#171717', display: 'flex', alignItems: 'center', padding: '0 24px'}}>
        <span style={{fontFamily: 'Mabry Pro, sans-serif', fontWeight: 700, fontSize: 28, color: '#fff'}}>Recents Chat</span>
      </div>
      {/* Chat List */}
      <div style={{flex: 1, width: '100%', display: 'flex', flexDirection: 'column', gap: 0, padding: '12px 0', alignItems: 'center', overflowY: 'auto'}}>
        {chatList.map((text, i) => (
          <ChatPreview key={i} text={text} expanded={true} />
        ))}
      </div>
      {/* New Chat Button */}
      <div style={{width: '100%', height: 64, borderBottomLeftRadius: 8, background: '#171717', display: 'flex', alignItems: 'center', padding: '0 24px'}}>
        <NewChatButton expanded={true} onClick={onNewChat} />
      </div>
    </aside>
  )
}

export default Sidebar 