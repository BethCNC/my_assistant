import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { ThumbnailImages } from './ThumbnailImages'

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
}

/**
 * Chat Input Component - Corrected based on Figma documentation
 * 
 * STRUCTURE (from Figma PDFs):
 * - Outer container: Gray background (#F7F7F7), black border, 8px radius, 16px padding
 * - Inner input: White background (#FFFFFF), state-dependent border, 4px radius, 12px 16px padding
 * - Layout: attachment icons → text input → character count → send button
 * 
 * STATES (from documentation):
 * - default: Black border (#000000) on outer, black border on inner
 * - hover: No visual change (hover state doesn't affect container)
 * - focused: Blue border (#2180EC) on inner input field only
 * - attaching: Gray border (#808080) on inner when panels open
 * 
 * MEASUREMENTS (from Figma PDFs):
 * - Outer container: 16px padding, 8px border radius, #F7F7F7 background
 * - Inner input: 12px 16px padding, 4px border radius, white background
 * - Icons: 20px size, 24px clickable area
 * - Text: Mabry Pro Medium 16px (#000000)
 * - Character count: Mabry Pro Regular 16px (#404040)
 */
export function ChatInput({ 
  placeholder = 'Ask me a question...',
  value = '',
  onChange,
  onSend,
  maxLength = 1000,
  disabled = false,
  className,
  initialState = 'default'
}: ChatInputProps) {
  const [inputValue, setInputValue] = useState(value)
  const [attachedImages, setAttachedImages] = useState<AttachedFile[]>([])
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([])
  const [isAttachingImages, setIsAttachingImages] = useState(false)
  const [isAttachingFiles, setIsAttachingFiles] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputValue])

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

  const addImage = () => {
    const variants = ['01', '02', '03', '04'] as const
    const newImage: AttachedFile = {
      id: `img_${Date.now()}`,
      name: `image${String(attachedImages.length + 1).padStart(3, '0')}.jpg`,
      type: 'image',
      thumbnailVariant: variants[Math.floor(Math.random() * variants.length)]
    }
    setAttachedImages([...attachedImages, newImage])
  }

  const addFile = () => {
    const newFile: AttachedFile = {
      id: `file_${Date.now()}`,
      name: 'document.docx',
      type: 'file'
    }
    setAttachedFiles([...attachedFiles, newFile])
  }

  const removeImage = (id: string) => {
    setAttachedImages(attachedImages.filter(img => img.id !== id))
  }

  const removeFile = (id: string) => {
    setAttachedFiles(attachedFiles.filter(file => file.id !== id))
  }

  // Get inner input border color based on state (from Figma)
  const getInputBorderColor = () => {
    if (isFocused) return '#2180EC' // Blue when focused
    if (isAttachingImages || isAttachingFiles) return '#808080' // Gray when attaching
    return '#000000' // Black by default
  }

  return (
    <div className={cn('relative', className)}>
      {/* Attaching Images Panel */}
      {isAttachingImages && (
        <div
          className="absolute bottom-full left-0 mb-2 z-10"
          style={{
            width: '275px',
            backgroundColor: '#FFF',
            border: '1px solid #BFBFBF',
            borderRadius: '8px',
            padding: '16px',
            boxShadow: '0px 4px 6px -1px rgba(0,0,0,0.1)'
          }}
        >
          <div className="flex items-center justify-between pb-2 mb-3" style={{ borderBottom: '1px solid #BFBFBF' }}>
            <span style={{ fontFamily: 'DM Sans', fontWeight: 500, fontSize: '14px', color: '#000' }}>Attached Images</span>
            <button
              onClick={addImage}
              style={{
                display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'DM Sans', fontWeight: 500, fontSize: '14px', color: '#808080', backgroundColor: '#F7F7F7', padding: '4px 8px', borderRadius: '4px', border: 'none', cursor: 'pointer'
              }}
            >
              Add <img src="/assets/icons/plus.svg" width={14} height={14} alt="Add" />
            </button>
          </div>
          <div className="space-y-2">
            {attachedImages.map((image, index) => (
              <div key={image.id} className="flex items-center justify-between" style={{padding: '8px 4px', borderRadius: '4px'}}>
                <div className="flex items-center gap-2">
                  <ThumbnailImages variant={image.thumbnailVariant || '01'} size={21} />
                  <span style={{ fontFamily: 'DM Sans', fontSize: '14px', color: '#000' }}>{image.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  {index === attachedImages.length - 1 && (
                    <span style={{ fontFamily: 'DM Sans', fontSize: '14px', color: '#2180EC' }}>12%</span>
                  )}
                  <button onClick={() => removeImage(image.id)} style={{display: 'flex', alignItems: 'center', border: 'none', background: 'none', cursor: 'pointer'}}>
                    <img src="/assets/icons/minus.svg" width={16} height={16} alt="Remove" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Attaching Files Panel */}
      {isAttachingFiles && (
        <div
          className="absolute bottom-full left-0 mb-2 z-10"
          style={{
            width: '275px',
            backgroundColor: '#FFF',
            border: '1px solid #BFBFBF',
            borderRadius: '8px',
            padding: '16px',
            boxShadow: '0px 4px 6px -1px rgba(0,0,0,0.1)'
          }}
        >
          <div className="flex items-center justify-between pb-2 mb-3" style={{ borderBottom: '1px solid #BFBFBF' }}>
            <span style={{ fontFamily: 'DM Sans', fontWeight: 500, fontSize: '14px', color: '#000' }}>Attached Files</span>
            <button
              onClick={addFile}
              style={{
                display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'DM Sans', fontWeight: 500, fontSize: '14px', color: '#808080', backgroundColor: '#F7F7F7', padding: '4px 8px', borderRadius: '4px', border: 'none', cursor: 'pointer'
              }}
            >
              Add <img src="/assets/icons/plus.svg" width={14} height={14} alt="Add" />
            </button>
          </div>
          <div className="space-y-2">
            {attachedFiles.map((file, index) => (
              <div key={file.id} className="flex items-center justify-between" style={{padding: '8px 4px', borderRadius: '4px'}}>
                <div className="flex items-center gap-2">
                  <img src="/assets/icons/files.svg" width={16} height={16} alt="File" />
                  <span style={{ fontFamily: 'DM Sans', fontSize: '14px', color: '#000' }}>{file.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  {index === attachedFiles.length - 1 && (
                    <span style={{ fontFamily: 'DM Sans', fontSize: '14px', color: '#2180EC' }}>12%</span>
                  )}
                  <button onClick={() => removeFile(file.id)} style={{display: 'flex', alignItems: 'center', border: 'none', background: 'none', cursor: 'pointer'}}>
                    <img src="/assets/icons/minus.svg" width={16} height={16} alt="Remove" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Container - Gray outer container (from Figma) */}
      <div
        style={{
          backgroundColor: '#F7F7F7',
          border: '2px solid #000',
          borderRadius: '8px',
          padding: '16px 12px',
          width: '740px',
          boxShadow: '0px 1px 2px 0px rgba(10,13,18,0.06), 0px 1px 1px 0px rgba(10,13,18,0.14)'
        }}
      >
        {/* Inner Input Field - White container with all elements (from Figma) */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#FFF',
            border: `1px solid ${getInputBorderColor()}`,
            borderRadius: '4px',
            padding: '10px 14px',
            gap: '8px',
            minHeight: '42px',
            width: '100%',
          }}
        >
          {/* Left: Attachment Icons - INSIDE the white input field */}
          <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
            <button
              onClick={() => {
                setIsAttachingFiles(!isAttachingFiles)
                setIsAttachingImages(false)
              }}
              style={{
                width: '24px', height: '24px', padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'none', border: 'none', borderRadius: '4px', cursor: 'pointer'
              }}
            >
              <img src="/assets/icons/files.svg" width={20} height={20} alt="Attach file" />
            </button>
            <button
              onClick={() => {
                setIsAttachingImages(!isAttachingImages)
                setIsAttachingFiles(false)
              }}
              style={{
                width: '24px', height: '24px', padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'none', border: 'none', borderRadius: '4px', cursor: 'pointer'
              }}
            >
              <img src="/assets/icons/images.svg" width={20} height={20} alt="Attach image" />
            </button>
          </div>

          {/* Center: Text Input - Takes remaining space */}
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
            className="flex-1 resize-none border-none outline-none bg-transparent"
            style={{
              fontFamily: 'Mabry Pro',
              fontWeight: 500,
              fontSize: '16px',
              color: '#000',
              minHeight: '22px',
              maxHeight: '100px',
              lineHeight: '1.25em',
            }}
          />

          {/* Right: Character Count + Send Button */}
          <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
            <span
              style={{
                fontFamily: 'Mabry Pro',
                fontWeight: 400,
                fontSize: '16px',
                color: '#404040',
                whiteSpace: 'nowrap',
              }}
            >
              {inputValue.length}/{maxLength}
            </span>
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() && attachedImages.length === 0 && attachedFiles.length === 0}
              style={{
                width: '24px', height: '24px', padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'none', border: 'none', borderRadius: '4px', cursor: inputValue.trim() || attachedImages.length > 0 || attachedFiles.length > 0 ? 'pointer' : 'not-allowed', opacity: inputValue.trim() || attachedImages.length > 0 || attachedFiles.length > 0 ? 1 : 0.5
              }}
            >
              <img src="/assets/icons/send.svg" width={20} height={20} alt="Send" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInput