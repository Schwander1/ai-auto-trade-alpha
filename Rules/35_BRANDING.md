# Branding Rules (Alpine Analytics)

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All Alpine Analytics assets (Web, PDF, Marketing, Social Media)

---

## Overview

This document defines the mandatory branding standards for Alpine Analytics LLC. All brand assets, designs, and implementations must follow these rules to maintain consistency and professional appearance.

---

## Brand Identity

### Company Information
- **Name:** Alpine Analytics LLC
- **Tagline:** Adaptive AI Trading Signals
- **Short Tagline:** Provably.
- **Trademark:** Alpine Analytics® (use ® in formal documentation)

### Brand Personality
- **Bold:** Confident, assertive, performance-driven
- **Trustworthy:** Professional, reliable, proof-centric
- **Modern Tech:** Futuristic, cutting-edge, innovative
- **Premium:** High-quality, polished, sophisticated

---

## Color System Rules

### Mandatory Color Palette

#### Background Colors (Black Scale)
- **Pure Black:** `#000000` - Deepest black
- **Primary:** `#0a0a0f` - Main backgrounds (MANDATORY for all UI)
- **Secondary:** `#0f0f1a` - Cards, surfaces, elevated elements
- **Tertiary:** `#15151a` - Higher elevation surfaces
- **Border:** `#1a1a2e` - Borders, dividers, separators

**Rule:** Never use gray backgrounds. Always use black scale.

#### Neon Accent Colors
- **Cyan:** `#18e0ff` - PRIMARY accent (CTAs, links, main highlights)
- **Pink:** `#fe1c80` - Secondary accent (highlights, secondary actions)
- **Purple:** `#9600ff` - Tertiary accent (special features, premium content)
- **Orange:** `#ff5f01` - Warnings, alerts, urgent CTAs

**Rule:** Use neon colors sparingly. Maximum 2 accent colors per component/page.

#### Gradients
- **Primary Gradient:** Cyan → Pink → Purple (90deg)
- **Cyan-Pink:** Cyan → Pink (90deg)
- **Pink-Purple:** Pink → Purple (90deg)

**Rule:** Use gradients for hero text, buttons, and major accents only.

#### Semantic Colors (Minority Use)
- **Success:** `#00ff88` - Profits, success states
- **Error:** `#ff2d55` - Losses, errors, critical alerts
- **Warning:** `#ff5f01` - Warnings (same as orange)
- **Info:** `#18e0ff` - Information (same as cyan)

**Rule:** Semantic colors should be <20% of total color usage.

### Color Usage Rules

1. **Dark First:** Always design for dark backgrounds
2. **Contrast:** Minimum 4.5:1 (AA) for normal text, 7:1 (AAA) preferred
3. **Accent Limit:** Maximum 2 neon colors per component
4. **No Light Backgrounds:** Never use white or light gray backgrounds
5. **Consistency:** Use brand colors from `alpine-frontend/lib/brand.ts` only

---

## Typography Rules

### Font Hierarchy

#### Display Font: Orbitron
- **Use:** Hero headlines, major titles, logotype
- **Weight:** 900 (Black) for maximum impact
- **Letter Spacing:** 0.15em (2-3px) - MANDATORY
- **Size:** 48px+ for hero, 36px+ for major headings
- **Style:** Futuristic, tech-forward, bold

**Rule:** Always use letter-spacing for Orbitron display text.

#### Heading Font: Montserrat
- **Use:** Section headers, subheadings, card titles
- **Weight:** 700 (Bold) or 600 (Semibold)
- **Size:** 24-30px for H2, 20-24px for H3
- **Style:** Modern, clean, professional

#### Body Font: Inter
- **Use:** Body text, UI elements, descriptions
- **Weight:** 400 (Regular) or 500 (Medium)
- **Size:** 16-18px minimum (desktop), 15-16px (mobile) - MANDATORY
- **Line Height:** 1.6 for readability
- **Style:** Readable, professional

**Rule:** Never use body text smaller than 15px.

#### Mono Font: JetBrains Mono
- **Use:** Code, data, technical content, hashes
- **Weight:** 400 (Regular)
- **Size:** 14-16px
- **Style:** Technical, precise

### Typography Rules

1. **Minimum Sizes:** 16px desktop, 15px mobile (body text)
2. **Line Height:** 1.6 for body text
3. **Letter Spacing:** 0.15em for Orbitron display text
4. **Font Stack:** Always include fallbacks
5. **No Custom Fonts:** Use only brand fonts

---

## Logo Rules

### Logo Variants

1. **Primary Logo** (`/brand/logo-primary.svg`)
   - Full color on black
   - Use: Main branding, headers, marketing

2. **Icon Logo** (`/brand/logo-icon.svg`)
   - 64x64px optimized
   - Use: Favicons, app icons, small spaces

3. **Wordmark** (`/brand/logo-wordmark.svg`)
   - Text only
   - Use: Text-only applications

### Logo Usage Rules

1. **Clear Space:** Minimum clear space = logo height
2. **Background:** Dark backgrounds only
3. **No Distortion:** Never stretch, rotate, or distort
4. **Trademark:** Include ® in formal documentation
5. **Minimum Size:** 24px height for icon, 40px for primary
6. **Color:** Never recolor or modify logo colors
7. **Placement:** Top-left (web), top-center (print)

---

## Layout & Spacing Rules

### Grid System
- **Columns:** 12-column responsive grid
- **Gap:** 24-32px between sections (MANDATORY)
- **Margins:** 24-32px for CTAs and info boxes

### Spacing Scale
- **XS:** 4px
- **SM:** 8px
- **MD:** 16px
- **LG:** 24px (preferred)
- **XL:** 32px (preferred for CTAs)
- **2XL:** 48px
- **3XL:** 64px

**Rule:** Use spacing scale consistently. Never use arbitrary values.

### Component Spacing
- **Cards:** 24px padding (1.5rem)
- **Sections:** 32px vertical spacing
- **Buttons:** 16px vertical, 32px horizontal padding
- **Modals:** 32px padding

---

## Effects & Animations Rules

### Neon Glow
- **Cyan:** `0 0 20px rgba(24, 224, 255, 0.5), 0 0 40px rgba(24, 224, 255, 0.3)`
- **Pink:** `0 0 20px rgba(254, 28, 128, 0.5), 0 0 40px rgba(254, 28, 128, 0.3)`
- **Purple:** `0 0 20px rgba(150, 0, 255, 0.5), 0 0 40px rgba(150, 0, 255, 0.3)`

**Rule:** Use glow effects sparingly. Maximum 3-5 elements per page.

### Pulse Animation
- **Duration:** 2s
- **Timing:** ease-in-out
- **Use:** Buttons, live stats, changing metrics
- **Effect:** Gentle opacity and glow intensity change

**Rule:** Maximum 2-3 pulsing elements per page.

### Hover Effects
- **Buttons:** Glow intensifies, slight lift (translateY -2px)
- **Cards:** Border glow increases
- **Links:** Underline with neon color

**Rule:** All interactive elements must have clear hover states.

---

## Component Rules

### Buttons
- **Primary:** Neon cyan background, black text, glow on hover
- **Secondary:** Neon pink outline, transparent background
- **CTA:** Orange for urgency, gradient for special
- **Padding:** 16px vertical, 32px horizontal
- **Font:** Montserrat Bold, 16px
- **Border Radius:** 8px

### Cards
- **Background:** `#0f0f1a` (secondary black)
- **Border:** 1px solid neon cyan (with glow)
- **Padding:** 24px
- **Shadow:** Soft with neon tint
- **Stats:** Orbitron font, large size, neon color

### Modals
- **Background:** `#0a0a0f` with backdrop blur
- **Border:** Neon cyan glow
- **Close Button:** Neon pink
- **Padding:** 32px

### Tables
- **Text:** White on dark background
- **Borders:** Neon borders for important cells
- **Shading:** Minimal
- **Hierarchy:** Clear with color coding

---

## PDF/Report Rules

### Headers
- **Background:** Black (`#0a0a0f`)
- **Headlines:** Large Orbitron (neon cyan)
- **Logo:** Top left
- **Date/Time:** Top right
- **Separator:** Neon line

### Sections
- **Separators:** Neon lines/borders
- **Spacing:** 32px between sections
- **Hierarchy:** Color-coded (cyan, pink, purple)

### Tables
- **Text:** White
- **Borders:** Neon for important data
- **Shading:** Minimal
- **Alignment:** Clear

---

## Social Media Rules

### Guidelines
- **Gradients:** Consistent with main palette
- **Hero Text:** Bold, Orbitron when possible
- **Tagline:** Include "Provably." when appropriate
- **Visual Anchors:** Icons, charts, or mini-mountains
- **Contrast:** High contrast for readability

### Templates
- **Instagram:** 1080x1080px
- **Twitter:** 1200x675px
- **LinkedIn:** 1200x627px
- **All:** Neon accents on black

---

## Accessibility Rules

### Contrast Requirements
- **AA Standard:** Minimum 4.5:1 for normal text
- **AAA Standard:** Minimum 7:1 for normal text (preferred)
- **Large Text:** Minimum 3:1 (AA) or 4.5:1 (AAA)

### Text Sizes
- **Minimum:** 16px for body text
- **Mobile:** 15-16px minimum
- **Desktop:** 16-18px preferred

### Focus States
- **Clear:** Glowing feedback on interactive elements
- **High Contrast:** Focus indicators
- **Keyboard:** Full keyboard navigation support

---

## Implementation Rules

### Code Standards

#### Frontend (Next.js/React)
```typescript
// ✅ CORRECT: Use brand config
import { AlpineBrand } from '@/lib/brand'
<div className="bg-alpine-black-primary text-alpine-neon-cyan">

// ❌ WRONG: Hardcoded colors
<div style={{ backgroundColor: '#0a0a0f' }}>
```

#### Tailwind CSS
```tsx
// ✅ CORRECT: Use Tailwind brand classes
<div className="bg-alpine-black-primary text-alpine-neon-cyan glow-cyan">

// ❌ WRONG: Custom colors
<div className="bg-[#0a0a0f] text-[#18e0ff]">
```

#### PDF Generation
```bash
# ✅ CORRECT: Use branded template
pandoc input.md -o output.pdf --template=scripts/pdf-template-alpine.tex

# ❌ WRONG: Generic template
pandoc input.md -o output.pdf
```

### Asset Generation

**Rule:** Always regenerate assets after brand changes:
```bash
node scripts/generate-brand-assets.js
```

This updates:
- CSS variables
- JSON config
- LaTeX colors
- Tailwind config (if needed)

---

## Quality Checklist

Before deploying any brand asset:

- [ ] Colors from brand config only
- [ ] Typography follows hierarchy
- [ ] Logo used correctly (clear space, no distortion)
- [ ] Spacing uses scale (24-32px preferred)
- [ ] Contrast meets AA/AAA standards
- [ ] Animations are subtle and purposeful
- [ ] Mobile responsive (15-16px minimum text)
- [ ] Accessibility tested
- [ ] Trademark symbol included (if formal doc)

---

## Violations & Enforcement

### Common Violations
1. Using light backgrounds
2. Text smaller than 15px
3. More than 2 accent colors per component
4. Missing letter-spacing on Orbitron
5. Hardcoded colors instead of brand config
6. Logo distortion or incorrect usage
7. Insufficient spacing (less than 24px)

### Enforcement
- **Code Review:** All brand changes require review
- **Automated Checks:** Linting for brand color usage
- **Design Review:** Visual assets require approval
- **Documentation:** All violations must be documented

---

## Updates & Versioning

### Brand Updates
1. Update `alpine-frontend/lib/brand.ts`
2. Run `node scripts/generate-brand-assets.js`
3. Update all components
4. Regenerate PDFs
5. Update Canva templates
6. Document changes

### Version Control
- **Brand Config:** Versioned in `brand.ts`
- **Assets:** Generated from config (not versioned)
- **Documentation:** This file tracks brand rules

---

## Related Rules

- [11_FRONTEND.md](11_FRONTEND.md) - Frontend implementation rules
- [08_DOCUMENTATION.md](08_DOCUMENTATION.md) - Documentation standards
- [26_API_DESIGN.md](26_API_DESIGN.md) - API design (for brand API)

---

## Resources

- **Brand Config:** `alpine-frontend/lib/brand.ts`
- **Brand Guide:** `docs/BRAND_STYLE_GUIDE_COMPLETE.md`
- **Quick Reference:** `docs/BRAND_QUICK_REFERENCE.md`
- **Canva Setup:** `scripts/CANVA_SETUP.md`
- **PDF Template:** `scripts/pdf-template-alpine.tex`

