# Alpine Analytics Branding System - Complete Setup Walkthrough

**Last Updated:** January 15, 2025  
**Version:** 1.0

---

## Overview

This walkthrough will guide you through the complete setup of the Alpine Analytics branding system, including logos, colors, typography, PDF generation, and Canva automation.

**Estimated Time:** 30-45 minutes  
**Prerequisites:** Node.js, Python 3.8+, AWS CLI configured

---

## Table of Contents

1. [Initial Setup](#1-initial-setup)
2. [Logo Creation](#2-logo-creation)
3. [Brand Configuration](#3-brand-configuration)
4. [Frontend Integration](#4-frontend-integration)
5. [PDF Generation Setup](#5-pdf-generation-setup)
6. [Canva API Integration](#6-canva-api-integration)
7. [Asset Generation](#7-asset-generation)
8. [Testing & Verification](#8-testing--verification)
9. [Next Steps](#9-next-steps)

---

## 1. Initial Setup

### Step 1.1: Verify Prerequisites

```bash
# Check Node.js (v18+ required)
node --version

# Check Python (v3.8+ required)
python3 --version

# Check AWS CLI (for Secrets Manager)
aws --version

# Check Pandoc (for PDF generation)
pandoc --version
```

### Step 1.2: Install Dependencies

```bash
# Navigate to workspace root
cd /Users/dylanneuenschwander/argo-alpine-workspace

# Install frontend dependencies
cd alpine-frontend
npm install

# Install Python dependencies for scripts
cd ../scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 1.3: Verify File Structure

Ensure these directories exist:
```
alpine-frontend/
├── lib/
│   └── brand.ts (should exist)
├── app/
│   └── globals.css
├── public/
│   └── brand/ (create if missing)
└── tailwind.config.ts

scripts/
├── canva_oauth2.py
├── canva_brand_automation.py
├── generate-brand-assets.js
├── pdf-template-alpine.tex
└── requirements.txt

docs/
└── (branding docs will go here)
```

---

## 2. Logo Creation

### Step 2.1: Create Logo Directory

```bash
mkdir -p alpine-frontend/public/brand
```

### Step 2.2: Verify Logo Files

The following SVG files should exist in `alpine-frontend/public/brand/`:

1. **logo-primary.svg** - Full logo with wordmark
2. **logo-icon.svg** - Icon only (64x64px)
3. **logo-wordmark.svg** - Text only
4. **logo-light.svg** - White version (if needed)
5. **logo-dark.svg** - Black version (if needed)

**Verify:**
```bash
ls -la alpine-frontend/public/brand/
```

---

## 3. Brand Configuration

### Step 3.1: Verify Brand Config

The brand config is located at `alpine-frontend/lib/brand.ts`. 

**Verify it includes:**
- All color palettes (black, neon, semantic, text)
- Typography system (fonts, sizes, weights, letter spacing)
- Spacing system
- Effects (glow, shadow, pulse)
- Logo paths
- Metadata

### Step 3.2: Verify Brand Config Export

```typescript
// Should export:
export const AlpineBrand
export const AlpineBrandJSON
export const brandColors
export const brandTypography
export const brandMetadata
```

---

## 4. Frontend Integration

### Step 4.1: Verify Tailwind Config

Check `alpine-frontend/tailwind.config.ts` includes:
- Brand colors (`alpine-black`, `alpine-neon`, etc.)
- Font families (Orbitron, Montserrat, Inter, JetBrains Mono)
- Letter spacing for display text
- Animations (pulse-neon, glow-pulse)
- Grid system

### Step 4.2: Verify Global CSS

Check `alpine-frontend/app/globals.css` includes:
- CSS variables for brand colors
- Font family variables
- Neon glow utilities
- Pulse animations
- Responsive typography

### Step 4.3: Install Fonts

Add fonts to `alpine-frontend/app/layout.tsx`:

```tsx
import { Orbitron, Montserrat, Inter, JetBrains_Mono } from 'next/font/google';

const orbitron = Orbitron({ 
  subsets: ['latin'],
  weight: ['400', '700', '900'],
  variable: '--font-orbitron',
});

const montserrat = Montserrat({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-montserrat',
});

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-inter',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400'],
  variable: '--font-mono',
});
```

---

## 5. PDF Generation Setup

### Step 5.1: Install LaTeX (if needed)

**macOS:**
```bash
brew install --cask mactex
# Or lightweight version:
brew install basictex
```

**Linux:**
```bash
sudo apt-get install texlive-full
```

**Verify:**
```bash
xelatex --version
```

### Step 5.2: Verify PDF Template

The template is at `scripts/pdf-template-alpine.tex`. 

**Verify it includes:**
- Brand colors defined
- Brand fonts (Inter, Montserrat, Orbitron)
- Black background
- Neon accent colors
- Logo placement
- Header/footer with branding

### Step 5.3: Test PDF Generation

```bash
# Create test markdown
echo "# Test Document\n\nThis is a test." > test.md

# Generate PDF
pandoc test.md -o test.pdf \
  --pdf-engine=xelatex \
  --template=scripts/pdf-template-alpine.tex

# Verify output
open test.pdf
```

---

## 6. Canva API Integration

### Step 6.1: Set Up Canva Credentials

```bash
# Run setup script
./scripts/setup-canva-credentials.sh

# Enter:
# - Client ID: OC-AZqFb4XOryzI
# - Client Secret: (your secret)
```

This stores credentials in AWS Secrets Manager:
- `alpine-analytics/canva-client-id`
- `alpine-analytics/canva-client-secret`

### Step 6.2: Configure Canva Integration

1. Go to [Canva Developers](https://www.canva.com/developers/)
2. Select your integration
3. Set redirect URI: `http://127.0.0.1:3000/auth/canva/callback`
4. Enable scopes:
   - `design:content:read`
   - `design:content:write`
   - `design:meta:read`

### Step 6.3: Authenticate

```bash
cd scripts
source venv/bin/activate

# Step 1: Get authorization URL
python3 canva_oauth2.py --auth

# Step 2: Visit URL in browser, authorize
# Step 3: Copy code from redirect URL

# Step 4: Exchange code for token
python3 canva_oauth2.py --code <CODE> --state <STATE>
```

### Step 6.4: Test API Connection

```bash
# List designs
python3 canva_oauth2.py --list-designs

# Test connection
python3 canva_oauth2.py --test
```

---

## 7. Asset Generation

### Step 7.1: Generate Brand Assets

```bash
# From workspace root
node scripts/generate-brand-assets.js
```

This generates:
- `alpine-frontend/app/brand-variables.css` - CSS variables
- `brand-config.json` - JSON export
- `scripts/alpine-brand-colors.tex` - LaTeX colors

### Step 7.2: Verify Generated Files

```bash
# Check CSS variables
cat alpine-frontend/app/brand-variables.css

# Check JSON config
cat brand-config.json

# Check LaTeX colors
cat scripts/alpine-brand-colors.tex
```

---

## 8. Testing & Verification

### Step 8.1: Frontend Testing

```bash
cd alpine-frontend

# Start dev server
npm run dev

# Verify:
# - Colors display correctly
# - Fonts load properly
# - Logo appears
# - Animations work
# - Responsive design
```

### Step 8.2: Brand Compliance Check

Create a test component:

```tsx
// app/test-brand.tsx
import { AlpineBrand } from '@/lib/brand';

export default function TestBrand() {
  return (
    <div className="bg-alpine-black-primary p-8">
      <h1 className="font-display text-6xl text-alpine-neon-cyan">
        Alpine Analytics
      </h1>
      <p className="text-alpine-text-primary mt-4">
        Brand system test
      </p>
    </div>
  );
}
```

### Step 8.3: PDF Testing

```bash
# Generate test PDF
pandoc docs/BRANDING_SYSTEM.md -o test-brand.pdf \
  --pdf-engine=xelatex \
  --template=scripts/pdf-template-alpine.tex

# Verify:
# - Black background
# - Neon colors
# - Brand fonts
# - Logo placement
```

### Step 8.4: Canva Testing

```bash
cd scripts
source venv/bin/activate

# Test API
python3 canva_oauth2.py --test

# List designs
python3 canva_oauth2.py --list-designs

# Generate asset (if template exists)
python3 canva_brand_automation.py \
  --generate-social <TEMPLATE_ID> \
  --title "Test" \
  --description "Test description"
```

---

## 9. Next Steps

### Immediate Actions

1. **Create Canva Templates**
   - Design branded templates in Canva
   - Save template IDs
   - Test automation

2. **Update Existing Components**
   - Replace hardcoded colors
   - Update typography
   - Add brand effects

3. **Generate Branded PDFs**
   - Update existing PDFs
   - Use branded template
   - Verify output

### Ongoing Maintenance

1. **Brand Updates**
   - Edit `alpine-frontend/lib/brand.ts`
   - Run `node scripts/generate-brand-assets.js`
   - Update components
   - Regenerate PDFs

2. **Asset Management**
   - Keep logo files in `public/brand/`
   - Version control brand config
   - Document changes

3. **Quality Assurance**
   - Regular brand audits
   - Accessibility checks
   - Performance monitoring

---

## Troubleshooting

### Common Issues

**Issue:** Fonts not loading
- **Solution:** Verify font imports in `layout.tsx`
- **Check:** Font files exist in `public/fonts/` (if self-hosted)

**Issue:** Colors not displaying
- **Solution:** Verify Tailwind config includes brand colors
- **Check:** CSS variables are generated

**Issue:** PDF generation fails
- **Solution:** Verify LaTeX installation
- **Check:** Template path is correct

**Issue:** Canva API errors
- **Solution:** Verify credentials in AWS Secrets Manager
- **Check:** Scopes are enabled in Canva

---

## Resources

- **Brand Rules:** `Rules/35_BRANDING.md`
- **Brand Guide:** `docs/BRAND_STYLE_GUIDE_COMPLETE.md`
- **Quick Reference:** `docs/BRAND_QUICK_REFERENCE.md`
- **Canva Setup:** `scripts/CANVA_SETUP.md`
- **Brand Config:** `alpine-frontend/lib/brand.ts`

---

## Support

For issues or questions:
1. Check troubleshooting section
2. Review brand rules document
3. Verify setup steps
4. Check logs for errors

---

**Setup Complete!** 🎉

Your Alpine Analytics branding system is now fully configured and ready to use.

