import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { ThumbnailImages } from './ThumbnailImages'
import { Icons } from './Icons'

interface AttachedFile {
  id: string
  name: string
  type: 'image' | 'file'
  progress?: number
  thumbnailVariant?: '01' | '02' | '03' | '04'
}

// Chat input states from Figma documentation
export type ChatInputState = 
  | 'default' 
  | 'hover' 
  | 'focused' 
  | 'attaching-images' 
  | 'attaching-files' 
  | 'images-attached' 
  | 'files-attached'

interface ChatInputProps {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSend?: (message: string, attachments: { images: AttachedFile[], files: AttachedFile[] }) => void
  maxLength?: number
  disabled?: boolean
  className?: string
  initialState?: ChatInputState
  variant?: ChatInputState
}

/**
 * Chat Input Component - Fixed with proper icons and layout
 * Based on Figma specifications and your screenshot layout
 */
export function ChatInput({ 
  placeholder = 'Ask me a question...',
  value = '',
  onChange,
  onSend,
  maxLength = 1000,
  disabled = false,
  className,
  initialState = 'default',
  variant: forcedVariant
}: ChatInputProps) {
  const [inputValue, setInputValue] = useState(value)
  const [attachedImages, setAttachedImages] = useState<AttachedFile[]>([])
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([])
  const [isAttachingImages, setIsAttachingImages] = useState(false)
  const [isAttachingFiles, setIsAttachingFiles] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const [hoverBtn, setHoverBtn] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Variant logic
  let variant: ChatInputState = 'default'
  if (forcedVariant) {
    variant = forcedVariant
  } else if (isAttachingImages) {
    variant = 'attaching-images'
  } else if (isAttachingFiles) {
    variant = 'attaching-files'
  } else if (attachedImages.length > 0) {
    variant = 'images-attached'
  } else if (attachedFiles.length > 0) {
    variant = 'files-attached'
  } else if (isFocused) {
    variant = 'focused'
  } else if (hoverBtn) {
    variant = 'hover'
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    if (newValue.length <= maxLength) {
      setInputValue(newValue)
      onChange?.(newValue)
    }
  }

  const handleSend = () => {
    if (inputValue.trim() || attachedImages.length > 0 || attachedFiles.length > 0) {
      onSend?.(inputValue.trim(), { images: attachedImages, files: attachedFiles })
      setInputValue('')
      setAttachedImages([])
      setAttachedFiles([])
      setIsAttachingImages(false)
      setIsAttachingFiles(false)
      onChange?.('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Get border color based on state
  const getBorderColor = () => {
    if (isFocused) return designTokens.colors.blue
    if (isAttachingImages || isAttachingFiles) return designTokens.colors.neutral[30]
    return designTokens.colors.black
  }

  // Button styles
  const getButtonStyle = (type: 'files' | 'images' | 'send') => {
    let isActive = false
    if (type === 'files' && (variant === 'attaching-files' || variant === 'files-attached')) isActive = true
    if (type === 'images' && (variant === 'attaching-images' || variant === 'images-attached')) isActive = true
    if (type === 'send' && (variant === 'focused' || hoverBtn === 'send')) isActive = true

    return {
      width: '44px',
      height: '44px',
      borderRadius: '8px',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: isActive ? designTokens.gradients.blue : designTokens.colors.black,
      transition: 'all 0.2s ease',
    }
  }

  return (
    <div className={cn('w-full flex flex-col', className)}>
      {/* Main input container */}
      <div
        style={{
          width: '100%',
          backgroundColor: designTokens.colors.neutral[10], // #F7F7F7 background
          border: `1px solid ${designTokens.colors.black}`,
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '8px', // Gap between input and button row
        }}
      >
        {/* Text input area */}
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          style={{
            width: '100%',
            backgroundColor: designTokens.colors.white,
            border: `1px solid ${getBorderColor()}`,
            borderRadius: '8px',
            padding: '12px 16px',
            fontFamily: designTokens.fonts.primary,
            fontSize: '16px',
            fontWeight: '500',
            color: designTokens.colors.black,
            outline: 'none',
            resize: 'none',
            minHeight: '48px',
            maxHeight: '120px',
            overflow: 'auto',
            transition: 'border-color 0.2s ease',
          }}
        />
      </div>

      {/* Button row - positioned BELOW input */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
        }}
      >
        {/* Left side - attachment buttons */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Files/paperclip button */}
          <button
            type="button"
            style={getButtonStyle('files')}
            onClick={() => {
              setIsAttachingFiles(!isAttachingFiles)
              setIsAttachingImages(false)
            }}
            onMouseEnter={() => setHoverBtn('files')}
            onMouseLeave={() => setHoverBtn('')}
          >
            <Icons 
              icon="paperclip" 
              size={24} 
              color={designTokens.colors.white}
            />
          </button>

          {/* Images/camera button */}
          <button
            type="button"
            style={getButtonStyle('images')}
            onClick={() => {
              setIsAttachingImages(!isAttachingImages)
              setIsAttachingFiles(false)
            }}
            onMouseEnter={() => setHoverBtn('images')}
            onMouseLeave={() => setHoverBtn('')}
          >
            <Icons 
              icon="camera" 
              size={24} 
              color={designTokens.colors.white}
            />
          </button>
        </div>

        {/* Right side - character count and send button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Character count */}
          <span
            style={{
              fontFamily: designTokens.fonts.primary,
              fontSize: '16px',
              fontWeight: '400',
              color: designTokens.colors.neutral[40], // #404040
            }}
          >
            {inputValue.length}/{maxLength}
          </span>

          {/* Send button */}
          <button
            type="button"
            style={getButtonStyle('send')}
            onClick={handleSend}
            disabled={!inputValue.trim() && attachedImages.length === 0 && attachedFiles.length === 0}
            onMouseEnter={() => setHoverBtn('send')}
            onMouseLeave={() => setHoverBtn('')}
          >
            <Icons 
              icon="send" 
              size={24} 
              color={designTokens.colors.white}
            />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInput