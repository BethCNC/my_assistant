import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { IconButton } from './IconButton'

// Chat input variants from Figma documentation
export type ChatInputVariant = 'default' | 'hover' | 'focused' | 'attaching_images' | 'attaching_files' | 'images_attached' | 'files_attached'

interface AttachedFile {
  name: string
  type: 'image' | 'file'
  progress?: number
}

interface ChatInputProps {
  variant?: ChatInputVariant
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSend?: (message: string) => void
  onAttachFiles?: () => void
  onAttachImages?: () => void
  attachedFiles?: AttachedFile[]
  onRemoveAttachment?: (index: number) => void
  maxLength?: number
  disabled?: boolean
  className?: string
}

/**
 * Chat Input Component - Based on Figma design system
 * Uses actual SVG icons from /assets/icons/
 * 
 * Measurements from Figma:
 * - Default height: 64px (calculated from design)
 * - Text: Mabry Pro Medium 16px (input text)
 * - Char count: Mabry Pro Regular 16px, color: neutral/40 (#404040)
 * - Background: neutral/10 (#F7F7F7) with border
 * - Input background: neutral/White (#FFFFFF)
 * 
 * States from Figma:
 * - default: Standard appearance
 * - hover: Subtle hover effect
 * - focused: Blue border (#2180EC)
 * - attaching_images/files: Shows attachment interface
 * - images_attached/files_attached: Shows attachment count
 */
export function ChatInput({ 
  variant = 'default',
  placeholder = 'Ask me a question...',
  value = '',
  onChange,
  onSend,
  onAttachFiles,
  onAttachImages,
  attachedFiles = [],
  onRemoveAttachment,
  maxLength = 1000,
  disabled = false,
  className 
}: ChatInputProps) {
  const [currentVariant, setCurrentVariant] = useState(variant)
  const [inputValue, setInputValue] = useState(value)

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    if (newValue.length <= maxLength) {
      setInputValue(newValue)
      onChange?.(newValue)
    }
  }

  const handleSend = () => {
    if (inputValue.trim() && onSend) {
      onSend(inputValue.trim())
      setInputValue('')
      onChange?.('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Get styles based on variant from Figma documentation
  const getVariantStyles = () => {
    switch (currentVariant) {
      case 'focused':
        return {
          containerBorder: `1px solid ${designTokens.colors.blue}`, // Blue border when focused
          inputBackground: designTokens.colors.white,
          inputBorder: `1px solid ${designTokens.colors.blue}`,
        }
      case 'hover':
        return {
          containerBorder: `1px solid ${designTokens.colors.black}`,
          inputBackground: designTokens.colors.white,
          inputBorder: `1px solid ${designTokens.colors.black}`,
        }
      case 'attaching_images':
      case 'attaching_files':
        return {
          containerBorder: `1px solid ${designTokens.colors.black}`,
          inputBackground: designTokens.colors.white,
          inputBorder: `1px solid ${designTokens.colors.neutral[30]}`, // #808080
        }
      default:
        return {
          containerBorder: `1px solid ${designTokens.colors.black}`,
          inputBackground: designTokens.colors.white,
          inputBorder: `1px solid ${designTokens.colors.black}`,
        }
    }
  }

  const styles = getVariantStyles()
  const imageAttachments = attachedFiles.filter(f => f.type === 'image')
  const fileAttachments = attachedFiles.filter(f => f.type === 'file')

  return (
    <div
      className={cn(
        'flex flex-col gap-2 transition-all duration-300',
        className
      )}
      style={{
        backgroundColor: designTokens.colors.neutral[10], // #F7F7F7 background
        border: styles.containerBorder,
        borderRadius: `${designTokens.radii.md}px`,
        padding: '12px',
      }}
    >
      {/* Image Attachment Area */}
      {(currentVariant === 'attaching_images' || imageAttachments.length > 0) && (
        <div
          className="border rounded-lg p-3"
          style={{
            backgroundColor: designTokens.colors.white,
            border: `1px solid ${designTokens.colors.neutral[20]}`, // #BFBFBF
          }}
        >
          {/* Header */}
          <div
            className="flex items-center justify-between pb-2 mb-2"
            style={{
              borderBottom: `1px solid ${designTokens.colors.neutral[20]}`,
            }}
          >
            <span
              style={{
                fontSize: '14px',
                fontFamily: designTokens.fonts.primary,
                fontWeight: 500,
                color: designTokens.colors.black,
              }}
            >
              Attached Images
            </span>
            <button
              onClick={() => onAttachImages?.()}
              className="text-sm text-neutral-30 hover:text-black"
              style={{
                fontSize: '14px',
                fontFamily: designTokens.fonts.primary,
                fontWeight: 500,
                color: designTokens.colors.neutral[30],
              }}
            >
              Add
            </button>
          </div>
          
          {/* Image list */}
          <div className="space-y-1">
            {imageAttachments.map((file, index) => (
              <div key={index} className="flex items-center justify-between">
                <span
                  style={{
                    fontSize: '14px',
                    fontFamily: designTokens.fonts.primary,
                    color: designTokens.colors.black,
                  }}
                >
                  {file.name}
                </span>
                {file.progress !== undefined ? (
                  <span
                    style={{
                      fontSize: '14px',
                      fontFamily: designTokens.fonts.primary,
                      color: designTokens.colors.blue,
                    }}
                  >
                    {file.progress}%
                  </span>
                ) : (
                  <button
                    onClick={() => onRemoveAttachment?.(index)}
                    className="hover:scale-110 transition-transform"
                  >
                    <IconButton variant="files" state="default" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File Attachment Area */}
      {(currentVariant === 'attaching_files' || fileAttachments.length > 0) && (
        <div
          className="border rounded-lg p-3"
          style={{
            backgroundColor: designTokens.colors.white,
            border: `1px solid ${designTokens.colors.neutral[20]}`, // #BFBFBF
          }}
        >
          {/* Header */}
          <div
            className="flex items-center justify-between pb-2 mb-2"
            style={{
              borderBottom: `1px solid ${designTokens.colors.neutral[20]}`,
            }}
          >
            <span
              style={{
                fontSize: '14px',
                fontFamily: designTokens.fonts.primary,
                fontWeight: 500,
                color: designTokens.colors.black,
              }}
            >
              Attached Files
            </span>
            <button
              onClick={() => onAttachFiles?.()}
              className="text-sm text-neutral-30 hover:text-black"
              style={{
                fontSize: '14px',
                fontFamily: designTokens.fonts.primary,
                fontWeight: 500,
                color: designTokens.colors.neutral[30],
              }}
            >
              Add
            </button>
          </div>
          
          {/* File list */}
          <div className="space-y-1">
            {fileAttachments.map((file, index) => (
              <div key={index} className="flex items-center justify-between">
                <span
                  style={{
                    fontSize: '14px',
                    fontFamily: designTokens.fonts.primary,
                    color: designTokens.colors.black,
                  }}
                >
                  {file.name}
                </span>
                {file.progress !== undefined ? (
                  <span
                    style={{
                      fontSize: '14px',
                      fontFamily: designTokens.fonts.primary,
                      color: designTokens.colors.blue,
                    }}
                  >
                    {file.progress}%
                  </span>
                ) : (
                  <button
                    onClick={() => onRemoveAttachment?.(index)}
                    className="hover:scale-110 transition-transform"
                  >
                    <IconButton variant="files" state="default" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Input Area */}
      <div
        className="flex items-end gap-3"
        style={{
          backgroundColor: styles.inputBackground,
          border: styles.inputBorder,
          borderRadius: `${designTokens.radii.md}px`,
          padding: '12px',
          minHeight: '64px',
        }}
      >
        {/* File attachment button using actual SVG */}
        <IconButton
          variant="files"
          state={fileAttachments.length > 0 ? 'attached' : 'default'}
          attachmentCount={fileAttachments.length}
          onClick={onAttachFiles}
        />

        {/* Image attachment button using actual SVG */}
        <IconButton
          variant="images"
          state={imageAttachments.length > 0 ? 'attached' : 'default'}
          attachmentCount={imageAttachments.length}
          onClick={onAttachImages}
        />

        {/* Text input */}
        <textarea
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setCurrentVariant('focused')}
          onBlur={() => setCurrentVariant(variant)}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none border-none outline-none bg-transparent"
          style={{
            fontSize: '16px', // Mabry Pro Medium 16px from Figma
            fontFamily: designTokens.fonts.primary,
            fontWeight: 500,
            color: designTokens.colors.black,
            minHeight: '24px',
            maxHeight: '120px',
          }}
        />

        {/* Character count */}
        <div
          className="flex items-center gap-3"
          style={{
            fontSize: '16px', // Mabry Pro Regular 16px from Figma
            fontFamily: designTokens.fonts.primary,
            color: designTokens.colors.neutral[40], // #404040 from Figma
          }}
        >
          <span>{inputValue.length}/{maxLength}</span>
        </div>

        {/* Send button using actual SVG */}
        <IconButton
          variant="send"
          state={inputValue.trim() ? 'hover' : 'default'}
          onClick={handleSend}
          disabled={!inputValue.trim() || disabled}
        />
      </div>
    </div>
  )
}

export default ChatInput
