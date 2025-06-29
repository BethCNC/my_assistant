'use client';

import React from 'react';
import { colors, typography, spacing, radius } from '../design-tokens/tokens';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  isFullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      isFullWidth = false,
      leftIcon,
      rightIcon,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    // Use CSS variables from design tokens
    const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
    
    // Map variant styles to design token variables
    const variantClasses = {
      primary: `bg-[${colors.primary[600]}] text-white hover:bg-[${colors.primary[700]}] focus:ring-[${colors.primary[500]}]`,
      secondary: `bg-[${colors.gray[200]}] text-[${colors.gray[900]}] hover:bg-[${colors.gray[300]}] focus:ring-[${colors.gray[500]}]`,
      outline: `border border-[${colors.gray[300]}] bg-transparent hover:bg-[${colors.gray[50]}] focus:ring-[${colors.gray[500]}]`,
      ghost: `bg-transparent hover:bg-[${colors.gray[100]}] focus:ring-[${colors.gray[500]}]`,
    };
    
    // Map size styles to design token variables
    const sizeClasses = {
      sm: `text-[${typography.fontSize.sm}] h-8 px-[${spacing.sm}] py-1 rounded-[${radius.sm}]`,
      md: `text-[${typography.fontSize.base}] h-10 px-[${spacing.md}] py-2 rounded-[${radius.md}]`,
      lg: `text-[${typography.fontSize.lg}] h-12 px-[${spacing.lg}] py-3 rounded-[${radius.lg}]`,
    };
    
    const widthClass = isFullWidth ? 'w-full' : '';
    
    const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${className}`;

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {leftIcon && !isLoading && <span className="mr-2">{leftIcon}</span>}
        {children}
        {rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button'; 