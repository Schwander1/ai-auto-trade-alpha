import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(214.3 31.8% 91.4%)",
        input: "hsl(214.3 31.8% 91.4%)",
        ring: "hsl(222.2 84% 4.9%)",
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // Alpine Design System - Official Brand Colors
        'alpine-black': {
          pure: '#000000',
          primary: '#0a0a0f',
          secondary: '#0f0f1a',
          tertiary: '#15151a',
          border: '#1a1a2e',
        },
        'alpine-neon': {
          cyan: '#18e0ff',
          cyanDark: '#00b8d4',
          pink: '#fe1c80',
          pinkDark: '#cc0066',
          purple: '#9600ff',
          purpleDark: '#5320f9',
          orange: '#ff5f01',
          orangeDark: '#cc4d00',
        },
        'alpine-gradient': {
          primary: 'linear-gradient(90deg, #18e0ff 0%, #fe1c80 50%, #9600ff 100%)',
          cyanPink: 'linear-gradient(90deg, #18e0ff 0%, #fe1c80 100%)',
          pinkPurple: 'linear-gradient(90deg, #fe1c80 0%, #9600ff 100%)',
          pulse: 'linear-gradient(135deg, #18e0ff 0%, #fe1c80 50%, #9600ff 100%)',
        },
        'alpine-semantic': {
          success: '#00ff88',
          error: '#ff2d55',
          warning: '#ff5f01',
          info: '#18e0ff',
        },
        'alpine-text': {
          primary: '#ffffff',
          secondary: '#a1a1aa',
          tertiary: '#71717a',
          inverse: '#000000',
        },
        // Legacy colors (for backward compatibility)
        'alpine-dark': '#000000',
        'alpine-darker': '#0a0a0f',
        'alpine-card': '#0f0f1a',
        'alpine-border': '#1a1a2e',
        'alpine-accent': '#18e0ff',
        'alpine-accent-dark': '#00b8d4',
        'alpine-pink': '#fe1c80',
        'alpine-pink-dark': '#cc0066',
        'alpine-blue': '#2962ff',
        'alpine-red': '#ff4560',
        'alpine-orange': '#ff9800',
        'alpine-text-dim': '#a1a1aa',
        'alpine-green': '#00ff88',
        'alpine-green-dark': '#00b8d4',
        black: '#000000',
        'space-gray': '#0F0F1E',
        'electric-cyan': '#18e0ff',
        'neon-pink': '#fe1c80',
        'neon-purple': '#9600ff',
        'laser-green': '#00ff88',
        'warning-red': '#ff2d55',
        'ice-blue': '#E0F7FF',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Orbitron', 'var(--font-display)', 'system-ui', 'sans-serif'],
        heading: ['Montserrat', 'var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
      },
      animation: {
        'pulse-glow-cyan': 'pulse-glow-cyan 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow-pink': 'pulse-glow-pink 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow-green': 'pulse-glow-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow-purple': 'pulse-glow-purple 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow-red': 'pulse-glow-red 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'fade-in': 'fade-in 0.6s ease-out',
        'slide-up': 'slide-up 0.6s ease-out',
        'count-up': 'count-up 2s ease-out',
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'neon-flicker': 'neon-flicker 3s ease-in-out infinite',
        'cursor-blink': 'cursor-blink 1s step-end infinite',
      },
      keyframes: {
        'pulse-glow-cyan': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(0, 240, 255, 0.5), 0 0 40px rgba(0, 240, 255, 0.3)' },
          '50%': { opacity: '0.9', boxShadow: '0 0 30px rgba(0, 240, 255, 0.8), 0 0 60px rgba(0, 240, 255, 0.5)' },
        },
        'pulse-glow-pink': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(255, 0, 110, 0.5), 0 0 40px rgba(255, 0, 110, 0.3)' },
          '50%': { opacity: '0.9', boxShadow: '0 0 30px rgba(255, 0, 110, 0.8), 0 0 60px rgba(255, 0, 110, 0.5)' },
        },
        'pulse-glow-green': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(0, 255, 136, 0.5), 0 0 40px rgba(0, 255, 136, 0.3)' },
          '50%': { opacity: '0.9', boxShadow: '0 0 30px rgba(0, 255, 136, 0.8), 0 0 60px rgba(0, 255, 136, 0.5)' },
        },
        'pulse-glow-purple': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(176, 38, 255, 0.5), 0 0 40px rgba(176, 38, 255, 0.3)' },
          '50%': { opacity: '0.9', boxShadow: '0 0 30px rgba(176, 38, 255, 0.8), 0 0 60px rgba(176, 38, 255, 0.5)' },
        },
        'pulse-glow-red': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(255, 45, 85, 0.5), 0 0 40px rgba(255, 45, 85, 0.3)' },
          '50%': { opacity: '0.9', boxShadow: '0 0 30px rgba(255, 45, 85, 0.8), 0 0 60px rgba(255, 45, 85, 0.5)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'count-up': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'neon-flicker': {
          '0%, 100%': { opacity: '1' },
          '41.99%': { opacity: '1' },
          '42%': { opacity: '0' },
          '43%': { opacity: '0' },
          '45%': { opacity: '1' },
          '46.99%': { opacity: '1' },
          '47%': { opacity: '0' },
          '49%': { opacity: '0' },
          '49.5%': { opacity: '1' },
          '50%': { opacity: '1' },
        },
        'cursor-blink': {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        'pulse-neon': {
          '0%, 100%': { 
            opacity: '1',
            boxShadow: '0 0 20px rgba(24, 224, 255, 0.5), 0 0 40px rgba(24, 224, 255, 0.3)'
          },
          '50%': { 
            opacity: '0.8',
            boxShadow: '0 0 30px rgba(24, 224, 255, 0.8), 0 0 60px rgba(24, 224, 255, 0.5)'
          },
        },
        'glow-pulse': {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(24, 224, 255, 0.5), 0 0 40px rgba(24, 224, 255, 0.3)'
          },
          '50%': { 
            boxShadow: '0 0 30px rgba(24, 224, 255, 0.8), 0 0 60px rgba(24, 224, 255, 0.5)'
          },
        },
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0, 240, 255, 0.5), 0 0 40px rgba(0, 240, 255, 0.3)',
        'glow-pink': '0 0 20px rgba(255, 0, 110, 0.5), 0 0 40px rgba(255, 0, 110, 0.3)',
        'glow-green': '0 0 20px rgba(0, 255, 136, 0.5), 0 0 40px rgba(0, 255, 136, 0.3)',
        'glow-purple': '0 0 20px rgba(176, 38, 255, 0.5), 0 0 40px rgba(176, 38, 255, 0.3)',
        'glow-red': '0 0 20px rgba(255, 45, 85, 0.5), 0 0 40px rgba(255, 45, 85, 0.3)',
      },
      backgroundImage: {
        'gradient-hero': 'linear-gradient(135deg, #000000 0%, #0F0F1E 50%, #1a0f2e 100%)',
        'gradient-cta': 'linear-gradient(90deg, #00F0FF 0%, #FF006E 100%)',
        'gradient-success': 'radial-gradient(circle at top, #00FF88 0%, transparent 70%)',
      },
    },
  },
  plugins: [],
}

export default config

