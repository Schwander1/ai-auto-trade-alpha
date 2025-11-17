/**
 * Alpine Analytics LLC - Official Brand System
 * Centralized brand configuration for all platforms
 * 
 * This is the SINGLE SOURCE OF TRUTH for all brand elements.
 * Update this file and run `node scripts/generate-brand-assets.js` to regenerate all assets.
 */

export const AlpineBrand = {
  // Official Color Palette - Neon on Black Theme
  colors: {
    // Backgrounds (Black Scale) - Deep blacks for drama
    black: {
      pure: '#000000',
      primary: '#0a0a0f',      // Main background (MANDATORY for all UI)
      secondary: '#0f0f1a',    // Cards/surfaces
      tertiary: '#15151a',     // Elevated surfaces
      border: '#1a1a2e',       // Borders/dividers
    },
    
    // Neon Accents (Primary Palette) - Bold and vibrant
    neon: {
      cyan: '#18e0ff',         // Primary accent - electric blue (CTAs, links, main highlights)
      cyanDark: '#00b8d4',     // Darker variant
      pink: '#fe1c80',         // Secondary accent - hot pink (highlights, secondary actions)
      pinkDark: '#cc0066',     // Darker variant
      purple: '#9600ff',       // Tertiary accent - violet (special features, premium content)
      purpleDark: '#5320f9',   // Darker variant
      orange: '#ff5f01',       // CTA/Warning accent (warnings, alerts, urgent CTAs)
      orangeDark: '#cc4d00',   // Darker variant
    },
    
    // Gradients for visual pulse
    gradients: {
      primary: 'linear-gradient(90deg, #18e0ff 0%, #fe1c80 50%, #9600ff 100%)',
      cyanPink: 'linear-gradient(90deg, #18e0ff 0%, #fe1c80 100%)',
      pinkPurple: 'linear-gradient(90deg, #fe1c80 0%, #9600ff 100%)',
      pulse: 'linear-gradient(135deg, #18e0ff 0%, #fe1c80 50%, #9600ff 100%)',
    },
    
    // Semantic Colors (Minority use - <20% of total color usage)
    semantic: {
      success: '#00ff88',      // Green for profits/success
      error: '#ff2d55',        // Red for losses/alerts
      warning: '#ff5f01',      // Orange for warnings
      info: '#18e0ff',         // Cyan for information
    },
    
    // Text Colors
    text: {
      primary: '#ffffff',      // Main text
      secondary: '#a1a1aa',    // Dimmed text
      tertiary: '#71717a',     // Muted text
      inverse: '#000000',      // Text on light backgrounds
    },
  },
  
  // Typography System - Optimized for readability
  typography: {
    fonts: {
      display: 'Orbitron',     // Headlines - futuristic, tech (letter-spacing: 2-3px)
      heading: 'Montserrat',   // Section headers - modern, clean (bold/semibold)
      body: 'Inter',           // Body text - readable, professional (16-18px min)
      mono: 'JetBrains Mono',  // Code/data - technical
    },
    sizes: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px (minimum for body)
      lg: '1.125rem',   // 18px (preferred body)
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
      '5xl': '3rem',     // 48px
      '6xl': '3.75rem',  // 60px
      '7xl': '4.5rem',   // 72px (hero)
    },
    weights: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
      black: 900,
    },
    letterSpacing: {
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
      display: '0.15em',  // For Orbitron display text (MANDATORY)
    },
  },
  
  // Spacing System - Generous spacing (24-32px preferred)
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px (preferred)
    xl: '2rem',      // 32px (preferred for CTAs)
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
  },
  
  // Grid System - 12-column responsive
  grid: {
    columns: 12,
    gap: {
      sm: '1rem',    // 16px
      md: '1.5rem',  // 24px
      lg: '2rem',    // 32px
    },
  },
  
  // Effects - Neon glow and pulse
  effects: {
    glow: {
      cyan: '0 0 20px rgba(24, 224, 255, 0.5), 0 0 40px rgba(24, 224, 255, 0.3), 0 0 60px rgba(24, 224, 255, 0.1)',
      pink: '0 0 20px rgba(254, 28, 128, 0.5), 0 0 40px rgba(254, 28, 128, 0.3), 0 0 60px rgba(254, 28, 128, 0.1)',
      purple: '0 0 20px rgba(150, 0, 255, 0.5), 0 0 40px rgba(150, 0, 255, 0.3), 0 0 60px rgba(150, 0, 255, 0.1)',
      orange: '0 0 20px rgba(255, 95, 1, 0.5), 0 0 40px rgba(255, 95, 1, 0.3)',
      gradient: '0 0 30px rgba(24, 224, 255, 0.4), 0 0 50px rgba(254, 28, 128, 0.3), 0 0 70px rgba(150, 0, 255, 0.2)',
    },
    shadow: {
      sm: '0 2px 8px rgba(0, 0, 0, 0.4)',
      md: '0 4px 16px rgba(0, 0, 0, 0.5)',
      lg: '0 8px 32px rgba(0, 0, 0, 0.6)',
      neon: '0 0 20px rgba(24, 224, 255, 0.3), 0 4px 16px rgba(0, 0, 0, 0.5)',
    },
    pulse: {
      duration: '2s',
      timing: 'ease-in-out',
    },
  },
  
  // Logo Specifications
  logo: {
    primary: '/brand/logo-primary.svg',      // Full color on black
    light: '/brand/logo-light.svg',          // White version
    dark: '/brand/logo-dark.svg',            // Black version
    icon: '/brand/logo-icon.svg',            // Icon only (64x64)
    wordmark: '/brand/logo-wordmark.svg',    // Text only
    favicon: '/brand/logo-icon.svg',         // For favicon
  },
  
  // Brand Metadata
  metadata: {
    name: 'Alpine Analytics LLC',
    tagline: 'Adaptive AI Trading Signals',
    taglineShort: 'Provably.',
    website: 'https://alpineanalytics.com',
    email: 'info@alpineanalytics.com',
    trademark: 'Alpine Analytics®',
  },
  
  // Animation Settings
  animations: {
    pulse: {
      duration: '2s',
      timing: 'ease-in-out',
      iteration: 'infinite',
    },
    fadeIn: {
      duration: '0.6s',
      timing: 'ease-out',
    },
    slideIn: {
      duration: '0.6s',
      timing: 'ease-out',
    },
  },
} as const;

// Export JSON version for use in other systems (PDF, Canva, etc.)
export const AlpineBrandJSON = JSON.stringify(AlpineBrand, null, 2);

// Export individual color palettes for easy access
export const brandColors = AlpineBrand.colors;
export const brandTypography = AlpineBrand.typography;
export const brandMetadata = AlpineBrand.metadata;

