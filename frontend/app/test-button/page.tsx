"use client"

import React, { useState } from 'react'
import { NewChatButton } from '@/components/figma-system/NewChatButton'
import { designTokens } from '@/lib/design-tokens'

/**
 * Test page for New Chat Button states
 * This allows us to verify all states match Figma documentation
 */
export default function NewChatButtonTest() {
  const [activeSize, setActiveSize] = useState<'full' | 'collapsed'>('full')

  return (
    <div 
      style={{ 
        minHeight: '100vh',
        padding: '40px',
        background: designTokens.gradients.rainbow,
        fontFamily: designTokens.fonts.primary,
      }}
    >
      <h1 style={{ 
        color: designTokens.colors.black,
        fontSize: '32px',
        fontWeight: 700,
        marginBottom: '32px'
      }}>
        New Chat Button - State Testing
      </h1>

      {/* Size Toggle */}
      <div style={{ marginBottom: '32px' }}>
        <button
          onClick={() => setActiveSize(activeSize === 'full' ? 'collapsed' : 'full')}
          style={{
            padding: '8px 16px',
            backgroundColor: designTokens.colors.blue,
            color: designTokens.colors.white,
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: 'pointer',
          }}
        >
          Current Size: {activeSize} (Click to toggle)
        </button>
      </div>

      {/* State Examples Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '32px',
        marginBottom: '40px',
      }}>
        {/* Default State */}
        <div style={{ 
          padding: '24px', 
          backgroundColor: 'rgba(255,255,255,0.9)', 
          borderRadius: '8px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}>
          <h3 style={{ margin: 0, color: designTokens.colors.black }}>Default State</h3>
          <p style={{ margin: 0, fontSize: '14px', color: designTokens.colors.neutral[40] }}>
            Fill: Black (#000000), Stroke: Black (#000000)
          </p>
          <NewChatButton 
            size={activeSize}
            state="default"
            onClick={() => console.log('Default clicked')}
          />
        </div>

        {/* Hover State */}
        <div style={{ 
          padding: '24px', 
          backgroundColor: 'rgba(255,255,255,0.9)', 
          borderRadius: '8px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}>
          <h3 style={{ margin: 0, color: designTokens.colors.black }}>Hover State</h3>
          <p style={{ margin: 0, fontSize: '14px', color: designTokens.colors.neutral[40] }}>
            Fill: Blue (#2180EC), Stroke: Blue (#2180EC)
          </p>
          <NewChatButton 
            size={activeSize}
            state="hover"
            onClick={() => console.log('Hover clicked')}
          />
        </div>

        {/* Focus State */}
        <div style={{ 
          padding: '24px', 
          backgroundColor: 'rgba(255,255,255,0.9)', 
          borderRadius: '8px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}>
          <h3 style={{ margin: 0, color: designTokens.colors.black }}>Focus State</h3>
          <p style={{ margin: 0, fontSize: '14px', color: designTokens.colors.neutral[40] }}>
            Fill: Blue (#2180EC), Stroke: Blue (#2180EC) + Focus Ring
          </p>
          <NewChatButton 
            size={activeSize}
            state="focus"
            onClick={() => console.log('Focus clicked')}
          />
        </div>

        {/* Active State */}
        <div style={{ 
          padding: '24px', 
          backgroundColor: 'rgba(255,255,255,0.9)', 
          borderRadius: '8px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}>
          <h3 style={{ margin: 0, color: designTokens.colors.black }}>Active State</h3>
          <p style={{ margin: 0, fontSize: '14px', color: designTokens.colors.neutral[40] }}>
            Fill: Blue Gradient (#69DEF2 to #126FD8)
          </p>
          <NewChatButton 
            size={activeSize}
            state="active"
            onClick={() => console.log('Active clicked')}
          />
        </div>
      </div>

      {/* Interactive Button */}
      <div style={{ 
        padding: '24px', 
        backgroundColor: 'rgba(255,255,255,0.9)', 
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <h3 style={{ margin: '0 0 16px 0', color: designTokens.colors.black }}>
          Interactive Button (Hover/Focus/Click to test)
        </h3>
        <NewChatButton 
          size={activeSize}
          onClick={() => console.log('Interactive button clicked!')}
        />
      </div>

      {/* Figma Specifications */}
      <div style={{ 
        marginTop: '40px',
        padding: '24px', 
        backgroundColor: 'rgba(0,0,0,0.9)', 
        borderRadius: '8px',
        color: designTokens.colors.white
      }}>
        <h3 style={{ margin: '0 0 16px 0' }}>Figma Specifications</h3>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          <li><strong>Size Full:</strong> 244px × 64px</li>
          <li><strong>Size Collapsed:</strong> 96px × 64px</li>
          <li><strong>Typography:</strong> Mabry Pro Bold 28px</li>
          <li><strong>Text Color:</strong> neutral/10 (#F7F7F7) - all states</li>
          <li><strong>Icon Size:</strong> 32px × 32px</li>
          <li><strong>Border Radius:</strong> 4px</li>
          <li><strong>Default:</strong> Fill & Stroke: Black (#000000)</li>
          <li><strong>Hover:</strong> Fill & Stroke: Blue (#2180EC)</li>
          <li><strong>Focus:</strong> Fill & Stroke: Blue (#2180EC) + Focus Ring</li>
          <li><strong>Active:</strong> Fill: Blue Gradient (#69DEF2 to #126FD8)</li>
        </ul>
      </div>
    </div>
  )
}