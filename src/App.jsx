import React from 'react'
import Sidebar from './Sidebar'
import ToolButton from './ToolButton'
import Suggestion from './Suggestion'
import ChatInput from './ChatInput'

const chatList = Array(8).fill('How can I better update...')
const suggestions = [
  {shape: 'asterisk.svg', text: 'I would like to know about design tokens'},
  {shape: 'asterisk.svg', text: 'How can I be most productive today?'},
  {shape: 'heart.svg', text: 'What are the most important tasks I should...'},
  {shape: 'star.svg', text: 'Can you help me convert this design file int...'},
  {shape: 'asterisk.svg', text: 'What is coming up in my medical calendar?'},
  {shape: 'clover.svg', text: 'Can you remember the business plan we we...'},
]
const tools = [
  {icon: 'icon-paperclip.svg', label: 'Notion'},
  {icon: 'icon-camera.svg', label: 'Figma'},
  {icon: 'icon-send.svg', label: 'Github'},
  {icon: 'icon-plus.svg', label: 'Email'},
  {icon: 'icon-arrow.svg', label: 'Calendar'},
]

const App = () => (
  <div
    style={{
      width: '100vw',
      height: '100vh',
      minHeight: 1024,
      minWidth: 1440,
      background: 'url(/assets/gradient.png) center/cover',
      display: 'flex',
      flexDirection: 'row',
      fontFamily: 'Mabry Pro, sans-serif',
    }}
  >
    {/* Sidebar */}
    <Sidebar chatList={chatList} onNewChat={() => {}} />
    {/* Main content */}
    <div style={{flex: 1, display: 'flex', flexDirection: 'column', padding: 40, gap: 32}}>
      {/* Header bar */}
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
          <img src='/assets/smiley.svg' alt='' style={{width: 40, height: 40}} />
          <span style={{fontWeight: 700, fontSize: 28, color: '#fff', letterSpacing: 1}}>BETH'S ASSISTANT</span>
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
          <span style={{fontWeight: 700, fontSize: 20, color: '#fff'}}>FRIDAY</span>
          <span style={{fontWeight: 700, fontSize: 20, color: '#fff'}}>JUNE 6, 2025</span>
          <span style={{fontWeight: 700, fontSize: 20, color: '#fff'}}>11:25 AM</span>
        </div>
      </div>
      {/* Tool buttons row */}
      <div style={{display: 'flex', gap: 24, marginBottom: 32}}>
        {tools.map(t => (
          <ToolButton key={t.label} icon={t.icon} label={t.label} />
        ))}
      </div>
      {/* Greeting */}
      <div style={{fontWeight: 700, fontSize: 32, color: '#171717', marginBottom: 24}}>
        Good Morning Beth!  What can I help you with today?
      </div>
      {/* Suggestions grid */}
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32}}>
        {suggestions.map((s, i) => (
          <Suggestion key={i} shape={s.shape} text={s.text} />
        ))}
      </div>
      {/* Chat input at bottom */}
      <div style={{marginTop: 'auto'}}>
        <ChatInput value='' onChange={() => {}} onSend={() => {}} />
      </div>
    </div>
  </div>
)

export default App 