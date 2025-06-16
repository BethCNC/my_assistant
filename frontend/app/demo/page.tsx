'use client'

import React, { useState } from 'react'
import { designTokens } from '@/lib/design-tokens'

// Import all our components
import IconButton from '@/components/figma-system/IconButton'
import NavigationText from '@/components/figma-system/NavigationText'
import ToolButton from '@/components/figma-system/ToolButton'
import NewChatButton from '@/components/figma-system/NewChatButton'
import ChatPreview from '@/components/figma-system/ChatPreview'
import { SuggestionCard } from '@/components/figma-system/SuggestionCard'
import { SuggestionShapes, getRandomShapes } from '@/components/figma-system/SuggestionShapes'
import { Sidebar } from '@/components/figma-system/Sidebar'
import { ChatInput } from '@/components/figma-system/ChatInput'
import Icons from '@/components/figma-system/Icons'

/**
 * Component Demo Page
 * Test all components from the Figma design system with actual SVG assets
 */
export default function ComponentDemo() {
  const [inputValue, setInputValue] = useState('')
  const [attachedFiles, setAttachedFiles] = useState([
    { name: 'document.pdf', type: 'file' as const },
    { name: 'image.jpg', type: 'image' as const },
  ])

  // Suggestion cards with dynamic shape changing
  const [suggestionTexts, setSuggestionTexts] = useState([
    'I would like to know about design tokens',
    'How do I create a component library?',
    'What are the best Figma plugins?',
    'Help me implement responsive design',
    'Explain design system architecture',
    'Guide me through Figma to code workflow',
  ])

  const sampleChats = [
    'How can I better update my design system?',
    'What are design tokens?',
    'How do I implement glassmorphism?',
    'Best practices for component libraries',
    'Figma to code workflow tips',
  ]

  // Function to randomize suggestion texts (triggers shape change)
  const randomizeSuggestions = () => {
    const suggestions = [
      'I would like to know about design tokens',
      'How do I create a component library?',
      'What are the best Figma plugins?',
      'Help me implement responsive design',
      'Explain design system architecture',
      'Guide me through Figma to code workflow',
      'Tell me about color theory',
      'How to organize design files?',
      'Best practices for naming conventions',
      'Accessibility in design systems',
      'Responsive design principles',
      'Component testing strategies',
    ]
    
    // Shuffle and pick 6 random suggestions
    const shuffled = suggestions.sort(() => 0.5 - Math.random())
    setSuggestionTexts(shuffled.slice(0, 6))
  }

  return (
    <div 
      className="min-h-screen p-8"
      style={{ 
        background: designTokens.gradients.rainbow,
        fontFamily: designTokens.fonts.primary,
      }}
    >
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="text-center mb-12">
          <h1 
            className="text-4xl font-black mb-4"
            style={{ color: designTokens.colors.white }}
          >
            Beth's Assistant Design System
          </h1>
          <p 
            className="text-lg mb-4"
            style={{ color: designTokens.colors.neutral[10] }}
          >
            Component Library Demo - Using Actual SVG Assets
          </p>
          <button
            onClick={randomizeSuggestions}
            className="px-6 py-2 bg-blue text-white rounded-lg hover:bg-blue/80 transition-all"
            style={{ backgroundColor: designTokens.colors.blue }}
          >
            🎲 Randomize Suggestion Shapes
          </button>
        </div>

        {/* Icons Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Icons (From /assets/icons/)</h2>
          <div className="flex gap-4 flex-wrap">
            {(['arrow', 'files', 'images', 'minus', 'plus', 'send', 'trash'] as const).map((icon) => (
              <div key={icon} className="flex flex-col items-center gap-2">
                <div className="p-3 bg-black rounded-lg">
                  <Icons icon={icon} color="white" />
                </div>
                <span className="text-sm text-white">{icon}.svg</span>
              </div>
            ))}
          </div>
        </section>

        {/* Suggestion Shapes Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Suggestion Shapes (From /assets/shapes/svg/)</h2>
          <div className="flex gap-4 flex-wrap">
            {([1, 2, 3, 4, 5, 6, 7] as const).map((shape) => (
              <div key={shape} className="flex flex-col items-center gap-2">
                <div className="p-3 bg-black rounded-lg">
                  <SuggestionShapes shape={shape} color="white" />
                </div>
                <span className="text-sm text-white">shape={shape}.svg</span>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-black/20 rounded-lg">
            <p className="text-white text-sm">
              <strong>Random Shapes:</strong> Each suggestion card automatically gets a random shape when the text changes.
              Click the "Randomize" button above to see shapes change dynamically!
            </p>
          </div>
        </section>

        {/* Icon Buttons Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Icon Buttons (Using Actual SVGs)</h2>
          <div className="space-y-4">
            <div className="flex gap-4 items-center">
              <IconButton variant="files" />
              <IconButton variant="files" state="hover" />
              <IconButton variant="files" state="attached" attachmentCount={3} />
            </div>
            <div className="flex gap-4 items-center">
              <IconButton variant="images" />
              <IconButton variant="images" state="hover" />
              <IconButton variant="images" state="attached" attachmentCount={2} />
            </div>
            <div className="flex gap-4 items-center">
              <IconButton variant="send" />
              <IconButton variant="send" state="focus" />
            </div>
          </div>
        </section>

        {/* Navigation Text Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Navigation Text (With Actual Smiley SVG)</h2>
          <div className="flex gap-8 items-center flex-wrap">
            <NavigationText word="smiley" />
            <NavigationText word="name" />
            <NavigationText word="day" />
            <NavigationText word="date" />
            <NavigationText word="time" />
          </div>
          <div className="mt-4 flex gap-8 items-center flex-wrap">
            <NavigationText word="day" state="hover" />
            <NavigationText word="date" state="hover" />
          </div>
          <div className="mt-4 p-4 bg-black/20 rounded-lg">
            <p className="text-white text-sm">
              <strong>Smiley Effect:</strong> The smiley uses /assets/smiley.svg (default) and /assets/smiley-gradient.svg (hover)
            </p>
          </div>
        </section>

        {/* Tool Buttons Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Tool Buttons</h2>
          <div className="flex gap-3 flex-wrap">
            {(['notion', 'figma', 'github', 'email', 'calendar'] as const).map((tool) => (
              <ToolButton key={tool} variant={tool} />
            ))}
          </div>
          <div className="flex gap-3 flex-wrap mt-4">
            <ToolButton variant="notion" state="hover" />
            <ToolButton variant="figma" state="focus" />
            <ToolButton variant="github" state="active" />
          </div>
        </section>

        {/* New Chat Buttons Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">New Chat Buttons</h2>
          <div className="flex gap-4 items-center">
            <NewChatButton size="full" />
            <NewChatButton size="collapsed" />
          </div>
          <div className="flex gap-4 items-center mt-4">
            <NewChatButton size="full" state="hover" />
            <NewChatButton size="collapsed" state="active" />
          </div>
        </section>

        {/* Chat Preview Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Chat Preview</h2>
          <div className="space-y-2">
            {sampleChats.slice(0, 3).map((chat, index) => (
              <ChatPreview
                key={index}
                message={chat}
                onClick={() => console.log('Chat selected:', chat)}
              />
            ))}
          </div>
        </section>

        {/* Suggestion Cards Section - WITH RANDOM SHAPES */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Suggestion Cards (With Random Shape Changes)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {suggestionTexts.map((text, index) => (
              <SuggestionCard 
                key={`${text}-${index}`} // Key includes text to trigger re-render
                text={text}
                state={index === 1 ? 'state3' : index === 2 ? 'focus' : 'default'}
                onClick={() => console.log('Suggestion clicked:', text)}
                randomizeShape={true} // Enable random shape changes
              />
            ))}
          </div>
          <div className="mt-4 p-4 bg-black/20 rounded-lg">
            <p className="text-white text-sm">
              <strong>Dynamic Shapes:</strong> Each card gets a random shape from /assets/shapes/svg/ when the text changes.
              The shape color changes based on the card state (default: black, state3: orange, focus: blue).
            </p>
          </div>
        </section>

        {/* Sidebar Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Sidebar</h2>
          <div className="flex gap-6">
            <Sidebar
              variant="default"
              recentChats={sampleChats}
              onNewChat={() => console.log('New chat clicked')}
              onChatSelect={(chat, index) => console.log('Chat selected:', chat, index)}
            />
            <Sidebar
              variant="collapsed"
              recentChats={sampleChats}
              onNewChat={() => console.log('New chat clicked')}
              onChatSelect={(chat, index) => console.log('Chat selected:', chat, index)}
            />
          </div>
        </section>

        {/* Chat Input Section */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Chat Input (With Actual Icons)</h2>
          <div className="space-y-6">
            {/* Default state */}
            <ChatInput
              value={inputValue}
              onChange={setInputValue}
              onSend={(message) => {
                console.log('Message sent:', message)
                setInputValue('')
              }}
              onAttachFiles={() => console.log('Attach files clicked')}
              onAttachImages={() => console.log('Attach images clicked')}
            />
            
            {/* With attachments */}
            <ChatInput
              variant="attaching_files"
              value="Here's my message with attachments"
              attachedFiles={attachedFiles}
              onRemoveAttachment={(index) => {
                const newFiles = [...attachedFiles]
                newFiles.splice(index, 1)
                setAttachedFiles(newFiles)
              }}
            />
          </div>
        </section>

        {/* Asset Reference */}
        <section className="bg-white/10 backdrop-blur-md rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Asset Files Used</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-white text-sm">
            <div>
              <h3 className="font-semibold mb-2">Icons (/assets/icons/)</h3>
              <ul className="space-y-1">
                <li>• arrow.svg</li>
                <li>• files.svg</li>
                <li>• images.svg</li>
                <li>• minus.svg</li>
                <li>• plus.svg</li>
                <li>• send.svg</li>
                <li>• trash.svg</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Shapes (/assets/shapes/svg/)</h3>
              <ul className="space-y-1">
                <li>• shape=1.svg through shape=7.svg</li>
                <li>• Used randomly in suggestion cards</li>
                <li>• Color filtered based on card state</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Other Assets</h3>
              <ul className="space-y-1">
                <li>• /assets/smiley.svg (default)</li>
                <li>• /assets/smiley-gradient.svg (hover)</li>
                <li>• /assets/gradient.png (background)</li>
              </ul>
            </div>
          </div>
        </section>

      </div>
    </div>
  )
}
