'use client';

import React from 'react';
import { colors, typography, radius } from '../design-tokens/tokens';

export type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';
export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  rounded?: boolean;
  icon?: React.ReactNode;
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      children,
      variant = 'default',
      size = 'md',
      rounded = false,
      icon,
      className = '',
      ...props
    },
    ref
  ) => {
    // Base classes
    const baseClasses = 'inline-flex items-center font-medium';
    
    // Variant classes using design tokens
    const variantClasses = {
      default: `bg-[${colors.gray[100]}] text-[${colors.gray[800]}]`,
      primary: `bg-[${colors.primary[100]}] text-[${colors.primary[800]}]`,
      success: `bg-[${colors.status.success}] text-white`,
      warning: `bg-[${colors.status.warning}] text-white`,
      error: `bg-[${colors.status.error}] text-white`,
      info: `bg-[${colors.status.info}] text-white`,
    };
    
    // Size classes using design tokens
    const sizeClasses = {
      sm: `text-[${typography.fontSize.xs}] px-2 py-0.5`,
      md: `text-[${typography.fontSize.sm}] px-2.5 py-0.5`,
      lg: `text-[${typography.fontSize.base}] px-3 py-1`,
    };
    
    // Rounded classes using design tokens
    const roundedClass = rounded ? `rounded-full` : `rounded-[${radius.sm}]`;
    
    const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${roundedClass} ${className}`;

    return (
      <span
        ref={ref}
        className={classes}
        {...props}
      >
        {icon && <span className="mr-1">{icon}</span>}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge'; 