// Enhanced design tokens based on your Figma design system
export const colors = {
  black: '#000000',
  white: '#ffffff',
  primary: '#fea2e4', // pink 500
  secondary: '#fcf261', // yellow 500
  accent: '#019cfe', // blue 500
  neutral: '#fafafa', // neutral 50
  error: '#f76b5a', // red 500
  success: '#75d46c', // green 500
}

export const radii = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 16,
  xl: 24,
  full: 9999,
}

export const fontSizes = {
  xs: 10,
  sm: 12,
  base: 16,
  md: 20,
  lg: 24,
  xl: 28,
  '2xl': 32,
  '3xl': 40,
  '4xl': 48,
  '5xl': 56,
}

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 40,
  '3xl': 48,
  '4xl': 64,
}

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
}

export const glassmorphism = {
  light: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  medium: {
    background: 'rgba(255, 255, 255, 0.15)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
  },
  dark: {
    background: 'rgba(0, 0, 0, 0.2)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  }
}