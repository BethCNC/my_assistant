import React from 'react'
import Sidebar from './Sidebar'
import ToolButton from './ToolButton'
import Suggestion from './Suggestion'
import ChatInput from './ChatInput'
import ChatConversation from './ChatConversation'
import { colors, radii, fontSizes, spacing } from './tokens'

const chatList = Array(8).fill('How can I better update...')

const suggestions = [
  {shape: 'asterisk', text: 'I would like to know about design tokens'},
  {shape: 'asterisk', text: 'I would like to know about design tokens'},
  {shape: 'heart', text: 'I would like to know about design tokens'},
  {shape: 'star', text: 'I would like to know about design tokens'},
  {shape: 'asterisk', text: 'I would like to know about design tokens'},
  {shape: 'clover', text: 'I would like to know about design tokens'},
]

const tools = [
  {icon: 'icon-paperclip.svg', label: 'Notion', active: true},
  {icon: 'icon-camera.svg', label: 'Figma', active: false},
  {icon: 'icon-send.svg', label: 'Github', active: false},
  {icon: 'icon-plus.svg', label: 'Email', active: false},
  {icon: 'icon-arrow.svg', label: 'Calendar', active: false},
]

const App = () => {
  const [inputValue, setInputValue] = React.useState('')
  const [currentView, setCurrentView] = React.useState('suggestions') // 'suggestions' or 'conversation'
  const [messages, setMessages] = React.useState([])
  
  const handleSuggestionClick = (text) => {
    setInputValue(text)
    setCurrentView('conversation')
    setMessages([
      {id: 1, sender: 'user', text, time: 'now'},
      {id: 2, sender: 'assistant', text: 'How can I help you with that?', time: 'now'}
    ])
  }

  const handleSend = () => {
    if (inputValue.trim()) {
      const newMessage = {id: messages.length + 1, sender: 'user', text: inputValue, time: 'now'}
      setMessages(prev => [...prev, newMessage])
      setCurrentView('conversation')
      setInputValue('')
    }
  }

  return (
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
      <Sidebar 
        chatList={chatList} 
        onNewChat={() => {
          setCurrentView('suggestions')
          setMessages([])
          setInputValue('')
        }} 
      />
      
      {/* Main content */}
      <div style={{
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        padding: spacing['2xl'], 
        gap: spacing.xl
      }}>
        
        {/* Header bar */}
        <div style={{
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          background: colors.black,
          borderRadius: radii.lg,
          padding: `${spacing.md}px ${spacing.lg}px`,
        }}>
          <div style={{
            display: 'flex', 
            alignItems: 'center', 
            gap: spacing.md
          }}>
            <img 
              src='/assets/smiley.svg' 
              alt='' 
              style={{
                width: 32,
                height: 32,
                filter: 'brightness(0) invert(1)',
              }}
            />
            <span 
              style={{
                fontWeight: 700, 
                fontSize: fontSizes['2xl'], 
                color: colors.white, 
                letterSpacing: '0.05em'
              }}
            >
              BETH'S ASSISTANT
            </span>
          </div>
          <div style={{
            display: 'flex', 
            alignItems: 'center', 
            gap: spacing.lg,
            color: colors.white,
            fontSize: fontSizes.lg,
            fontWeight: 700
          }}>
            <span>FRIDAY</span>
            <span>JUNE 6, 2025</span>
            <span>11:25 AM</span>
          </div>
        </div>
        
        {/* Tool buttons row */}
        <div style={{
          display: 'flex', 
          gap: spacing.lg
        }}>
          {tools.map(t => (
            <ToolButton 
              key={t.label} 
              icon={t.icon} 
              label={t.label} 
              active={t.active}
            />
          ))}
        </div>
        
        {/* Main content area */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: spacing.xl,
        }}>
          {currentView === 'suggestions' ? (
            <>
              {/* Greeting */}
              <h2 style={{
                color: colors.white,
                fontSize: fontSizes['4xl'], // Much larger text
                fontWeight: 400,
                margin: 0,
                textAlign: 'center',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              }}>
                Good Morning Beth! What can I help you with today?
              </h2>
              
              {/* Suggestions Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: spacing.lg,
                maxWidth: 800,
                margin: '0 auto',
                width: '100%',
              }}>
                {suggestions.map((suggestion, index) => (
                  <Suggestion
                    key={index}
                    shape={suggestion.shape}
                    text={suggestion.text}
                    onClick={() => handleSuggestionClick(suggestion.text)}
                    index={index}
                  />
                ))}
              </div>
            </>
          ) : (
            /* Chat conversation area */
            <ChatConversation 
              messages={messages} 
              onBack={() => setCurrentView('suggestions')}
            />
          )}
          
          {/* Chat input at bottom */}
          <div style={{ marginTop: 'auto' }}>
            <ChatInput 
              value={inputValue} 
              onChange={(e) => setInputValue(e.target.value)} 
              onSend={handleSend} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App