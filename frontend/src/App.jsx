import React from 'react'
import Sidebar from './Sidebar'
import ToolButton from './ToolButton'
import Suggestion from './Suggestion'
import ChatInput from './ChatInput'
import ChatConversation from './ChatConversation'

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

const messages = [
  {id: 1, sender: 'assistant', text: 'How can I help you today, Beth?', time: '10 Min ago'},
  {id: 2, sender: 'user', text: 'I want to learn about UI design systems and how to build them in FIgms.', time: '12 Min ago'},
  {id: 3, sender: 'assistant', text: 'Sure I can help you learn all about design systems in Figma. Where would you like to start?', time: '10 Min ago'},
  {id: 4, sender: 'user', text: 'Let's start by learning about figma variable collections and best practices for setting them up in terms of how many collections you should have and what types and what they should contain.', time: '12 Min ago'},
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
      {/* Chat conversation area */}
      <ChatConversation messages={messages} />
      {/* Chat input at bottom */}
      <div style={{marginTop: 'auto'}}>
        <ChatInput value='' onChange={() => {}} onSend={() => {}} />
      </div>
    </div>
  </div>
)

export default App 