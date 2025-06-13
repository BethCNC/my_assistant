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
  variant?: ChatInputState
}

const ICON_BTN_SIZE = 44
const ICON_SIZE = 24

const iconBtnStyle = (bg: string) => ({
  width: ICON_BTN_SIZE,
  height: ICON_BTN_SIZE,
  borderRadius: 8,
  background: bg,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  border: 'none',
  padding: 0,
  cursor: 'pointer',
  transition: 'background 0.15s',
})

const blueGradient = 'linear-gradient(90deg, #69DEF2 0%, #126FD8 100%)'

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

  // Icon button backgrounds by variant/state
  const filesBtnBg =
    variant === 'attaching-files' || variant === 'files-attached'
      ? blueGradient
      : '#000'
  const imagesBtnBg =
    variant === 'attaching-images' || variant === 'images-attached'
      ? blueGradient
      : '#000'
  const sendBtnBg =
    variant === 'focused' || variant === 'hover' || variant === 'attaching-images' || variant === 'attaching-files' || variant === 'images-attached' || variant === 'files-attached'
      ? blueGradient
      : '#000'

  // Border for textarea
  let border = '2px solid #000'
  if (variant === 'focused') border = '2px solid #2180EC'
  if (variant === 'hover') border = '2px solid #2180EC'
  if (variant === 'attaching-images' || variant === 'attaching-files') border = '2px solid #808080'

  // Attachment popovers
  const showImagesPanel = variant === 'attaching-images'
  const showFilesPanel = variant === 'attaching-files'

  // Images attached badge
  const showImagesBadge = variant === 'images-attached'
  // Files attached badge
  const showFilesBadge = variant === 'files-attached'

  return (
    <div className={cn('w-full flex flex-col items-center', className)} style={{gap: 8}}>
      {/* Textarea */}
      <div style={{width: 600}}>
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          disabled={disabled}
          rows={3}
          style={{
            width: '100%',
            fontFamily: 'Mabry Pro',
            fontWeight: 500,
            fontSize: 16,
            color: '#000',
            border,
            borderRadius: 8,
            padding: '18px 20px',
            outline: 'none',
            resize: 'none',
            background: '#fff',
            minHeight: 80,
            boxSizing: 'border-box',
            transition: 'border 0.15s',
          }}
        />
      </div>
      {/* Controls Row */}
      <div style={{width: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8}}>
        {/* Left: Icon Buttons */}
        <div style={{display: 'flex', gap: 8, position: 'relative'}}>
          {/* Files Button */}
          <button
            type="button"
            style={iconBtnStyle(filesBtnBg)}
            onClick={() => {
              setIsAttachingFiles(!isAttachingFiles)
              setIsAttachingImages(false)
            }}
            onMouseEnter={()=>setHoverBtn('files')}
            onMouseLeave={()=>setHoverBtn('')}
          >
            <img src="/assets/icons/files.svg" width={ICON_SIZE} height={ICON_SIZE} alt="Attach file" style={{filter: 'brightness(0) invert(1)'}} />
            {/* Files badge */}
            {showFilesBadge && (
              <span style={{position: 'absolute', right: -8, top: -8, background: blueGradient, color: '#fff', borderRadius: 8, fontSize: 16, fontWeight: 700, padding: '2px 8px', minWidth: 24, textAlign: 'center', fontFamily: 'Mabry Pro', border: '2px solid #fff'}}>
                {attachedFiles.length}
              </span>
            )}
          </button>
          {/* Images Button */}
          <button
            type="button"
            style={iconBtnStyle(imagesBtnBg)}
            onClick={() => {
              setIsAttachingImages(!isAttachingImages)
              setIsAttachingFiles(false)
            }}
            onMouseEnter={()=>setHoverBtn('images')}
            onMouseLeave={()=>setHoverBtn('')}
          >
            <img src="/assets/icons/images.svg" width={ICON_SIZE} height={ICON_SIZE} alt="Attach image" style={{filter: 'brightness(0) invert(1)'}} />
            {/* Images badge/thumbnails */}
            {showImagesBadge && attachedImages.length > 0 && (
              <div style={{position: 'absolute', left: '100%', top: 0, display: 'flex', alignItems: 'center', gap: 2}}>
                {attachedImages.slice(0,2).map((img, i) => (
                  <ThumbnailImages key={img.id} variant={img.thumbnailVariant || '01'} size={22} />
                ))}
                {attachedImages.length > 2 && (
                  <span style={{background: blueGradient, color: '#fff', borderRadius: 8, fontSize: 12, fontWeight: 700, padding: '2px 6px', fontFamily: 'Mabry Pro', border: '2px solid #fff', marginLeft: 2}}>
                    +{attachedImages.length - 2}
                  </span>
                )}
              </div>
            )}
          </button>
          {/* Images Panel */}
          {showImagesPanel && (
            <div style={{position: 'absolute', top: -180, left: 0, width: 275, background: '#fff', border: '1px solid #BFBFBF', borderRadius: 8, padding: 16, boxShadow: '0px 4px 6px -1px rgba(0,0,0,0.1)', zIndex: 10}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #BFBFBF', paddingBottom: 8, marginBottom: 12}}>
                <span style={{fontFamily: 'DM Sans', fontWeight: 500, fontSize: 14, color: '#000'}}>Attached Images</span>
                <button onClick={addImage} style={{display: 'flex', alignItems: 'center', gap: 4, fontFamily: 'DM Sans', fontWeight: 500, fontSize: 14, color: '#808080', background: '#F7F7F7', padding: '4px 8px', borderRadius: 4, border: 'none', cursor: 'pointer'}}>Add <img src="/assets/icons/plus.svg" width={14} height={14} alt="Add" /></button>
              </div>
              <div style={{display: 'flex', flexDirection: 'column', gap: 8}}>
                {attachedImages.map((image, index) => (
                  <div key={image.id} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 4px', borderRadius: 4}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                      <ThumbnailImages variant={image.thumbnailVariant || '01'} size={21} />
                      <span style={{fontFamily: 'DM Sans', fontSize: 14, color: '#000'}}>{image.name}</span>
                    </div>
                    <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                      {index === attachedImages.length - 1 && <span style={{fontFamily: 'DM Sans', fontSize: 14, color: '#2180EC'}}>12%</span>}
                      <button onClick={() => removeImage(image.id)} style={{display: 'flex', alignItems: 'center', border: 'none', background: 'none', cursor: 'pointer'}}><img src="/assets/icons/minus.svg" width={16} height={16} alt="Remove" /></button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Files Panel */}
          {showFilesPanel && (
            <div style={{position: 'absolute', top: -180, left: 0, width: 275, background: '#fff', border: '1px solid #BFBFBF', borderRadius: 8, padding: 16, boxShadow: '0px 4px 6px -1px rgba(0,0,0,0.1)', zIndex: 10}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #BFBFBF', paddingBottom: 8, marginBottom: 12}}>
                <span style={{fontFamily: 'DM Sans', fontWeight: 500, fontSize: 14, color: '#000'}}>Attached Files</span>
                <button onClick={addFile} style={{display: 'flex', alignItems: 'center', gap: 4, fontFamily: 'DM Sans', fontWeight: 500, fontSize: 14, color: '#808080', background: '#F7F7F7', padding: '4px 8px', borderRadius: 4, border: 'none', cursor: 'pointer'}}>Add <img src="/assets/icons/plus.svg" width={14} height={14} alt="Add" /></button>
              </div>
              <div style={{display: 'flex', flexDirection: 'column', gap: 8}}>
                {attachedFiles.map((file, index) => (
                  <div key={file.id} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 4px', borderRadius: 4}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                      <img src="/assets/icons/files.svg" width={16} height={16} alt="File" />
                      <span style={{fontFamily: 'DM Sans', fontSize: 14, color: '#000'}}>{file.name}</span>
                    </div>
                    <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                      {index === attachedFiles.length - 1 && <span style={{fontFamily: 'DM Sans', fontSize: 14, color: '#2180EC'}}>12%</span>}
                      <button onClick={() => removeFile(file.id)} style={{display: 'flex', alignItems: 'center', border: 'none', background: 'none', cursor: 'pointer'}}><img src="/assets/icons/minus.svg" width={16} height={16} alt="Remove" /></button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        {/* Right: Char count + Send */}
        <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
          <span style={{fontFamily: 'Mabry Pro', fontWeight: 400, fontSize: 16, color: '#404040'}}>
            {inputValue.length}/{maxLength}
          </span>
          <button
            type="button"
            style={iconBtnStyle(sendBtnBg)}
            onClick={handleSend}
            disabled={!inputValue.trim() && attachedImages.length === 0 && attachedFiles.length === 0}
            onMouseEnter={()=>setHoverBtn('send')}
            onMouseLeave={()=>setHoverBtn('')}
          >
            <img src="/assets/icons/send.svg" width={ICON_SIZE} height={ICON_SIZE} alt="Send" style={{filter: 'brightness(0) invert(1)'}} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInput