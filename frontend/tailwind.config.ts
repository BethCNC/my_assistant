import type { Config } from "tailwindcss";
import { designTokens } from "./lib/design-tokens";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      // Use design tokens from Figma
      colors: {
        // Figma brand colors
        orange: designTokens.colors.orange,
        blue: designTokens.colors.blue,
        
        // Figma neutral scale
        white: designTokens.colors.white,
        neutral: designTokens.colors.neutral,
        black: designTokens.colors.black,
        
        // Keep shadcn/ui colors for compatibility
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        },
        sidebar: {
          DEFAULT: 'hsl(var(--sidebar-background))',
          foreground: 'hsl(var(--sidebar-foreground))',
          primary: 'hsl(var(--sidebar-primary))',
          'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
          accent: 'hsl(var(--sidebar-accent))',
          'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
          border: 'hsl(var(--sidebar-border))',
          ring: 'hsl(var(--sidebar-ring))'
        }
      },
      
      // Figma spacing scale
      spacing: designTokens.spacing,
      
      // Figma border radius
      borderRadius: {
        ...designTokens.radii,
        // Keep shadcn/ui radius for compatibility
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      
      // Figma font sizes
      fontSize: designTokens.fontSizes,
      
      // Figma font families
      fontFamily: {
        primary: ['Mabry Pro', 'sans-serif'],
        greeting: ['Behind The Nineties', 'serif'],
        sans: ['Mabry Pro', 'sans-serif'], // Override default sans
      },
      
      // Figma box shadows
      boxShadow: {
        // Figma shadows
        'button': designTokens.shadows.button,
        'inner-100': designTokens.shadows.inner[100],
        'inner-200': designTokens.shadows.inner[200],
        'inner-300': designTokens.shadows.inner[300],
        'inner-400': designTokens.shadows.inner[400],
        'inner-500': designTokens.shadows.inner[500],
        'inner-600': designTokens.shadows.inner[600],
        'drop-glow': designTokens.shadows.drop.glow,
        'drop-sm': designTokens.shadows.drop.sm,
      },
      
      // Figma background images
      backgroundImage: {
        'gradient-rainbow': designTokens.gradients.rainbow,
        'gradient-blue': designTokens.gradients.blue,
      },
      
      // Figma backdrop blur
      backdropBlur: {
        'overlay': '2px',
        'glass': '2px',
      },
      
      // Figma blur
      blur: {
        'layer': '2px',
      },
      
      keyframes: {
        'accordion-down': {
          from: {
            height: '0'
          },
          to: {
            height: 'var(--radix-accordion-content-height)'
          }
        },
        'accordion-up': {
          from: {
            height: 'var(--radix-accordion-content-height)'
          },
          to: {
            height: '0'
          }
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
