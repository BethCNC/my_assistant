import React from 'react'

export interface ToastProps {
  variant?: 'default' | 'destructive'
  title?: string
  description?: string
  action?: ToastActionElement
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export interface ToastActionElement {
  altText: string
  onClick: () => void
}

export const Toast = ({ variant = 'default', title, description, action }: ToastProps) => {
  return (
    <div
      style={{
        padding: '16px',
        borderRadius: '8px',
        backgroundColor: variant === 'destructive' ? '#ef4444' : '#f7f7f7',
        color: variant === 'destructive' ? 'white' : 'black',
        border: '1px solid #e5e7eb',
        maxWidth: '400px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      }}
    >
      {title && (
        <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
          {title}
        </div>
      )}
      {description && (
        <div style={{ fontSize: '14px' }}>
          {description}
        </div>
      )}
      {action && (
        <button
          onClick={action.onClick}
          style={{
            marginTop: '8px',
            padding: '4px 8px',
            backgroundColor: 'transparent',
            border: '1px solid currentColor',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {action.altText}
        </button>
      )}
    </div>
  )
}

export default Toast 