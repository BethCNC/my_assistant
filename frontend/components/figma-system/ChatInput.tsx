import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { designTokens } from '@/lib/design-tokens'
import { ThumbnailImages } from './ThumbnailImages'
import { Icons } from './Icons'
import Image from 'next/image'
import styles from './ChatInput.module.css'

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

  // Figma: attached dropdown
  const showImagesDropdown = isAttachingImages || (attachedImages.length > 0 && !isAttachingImages)
  const showFilesDropdown = isAttachingFiles || (attachedFiles.length > 0 && !isAttachingFiles)

  return (
    <div
      className={styles.container}
      style={{borderColor: getBorderColor(), background: designTokens.colors.neutral[10]}}
      onMouseEnter={() => setHoverBtn('send')}
      onMouseLeave={() => setHoverBtn('')}
    >
      <textarea
        ref={textareaRef}
        className={styles.textarea}
        placeholder={placeholder}
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        maxLength={maxLength}
        rows={3}
        style={{fontFamily: designTokens.fonts.primary}}
      />
      <div className={styles.controls}>
        <button type="button" className={styles.iconBtn} onClick={() => {
          setIsAttachingFiles(!isAttachingFiles)
          setIsAttachingImages(false)
        }}>
          <Image src="/assets/icons/files.svg" width={24} height={24} alt="Attach files" />
        </button>
        <button type="button" className={styles.iconBtn} onClick={() => {
          setIsAttachingImages(!isAttachingImages)
          setIsAttachingFiles(false)
        }}>
          <Image src="/assets/icons/images.svg" width={24} height={20} alt="Attach images" />
        </button>
        <span className={styles.charCount}>{inputValue.length}/{maxLength}</span>
        <button type="button" className={styles.iconBtnSend} onClick={handleSend}>
          <Image src="/assets/icons/send.svg" width={24} height={22} alt="Send" />
        </button>
      </div>
      {/* Attached Images Dropdown */}
      {showImagesDropdown && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>Attached Images</div>
          {attachedImages.map((img, i) => (
            <div className={styles.dropdownItem} key={i}>
              <div className={styles.thumb}><Image src={img.src} width={21} height={21} alt={img.name} /></div>
              <div className={styles.fileName}>{img.name}</div>
              {img.progress && <div className={styles.progress}>{img.progress}%</div>}
              <button className={styles.removeBtn}>&minus;</button>
            </div>
          ))}
        </div>
      )}
      {/* Attached Files Dropdown */}
      {showFilesDropdown && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>Attached Files</div>
          {attachedFiles.map((file, i) => (
            <div className={styles.dropdownItem} key={i}>
              <div className={styles.fileIcon}><Image src="/assets/icons/files.svg" width={21} height={21} alt="file" /></div>
              <div className={styles.fileName}>{file.name}</div>
              {file.progress && <div className={styles.progress}>{file.progress}%</div>}
              <button className={styles.removeBtn}>&minus;</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ChatInput