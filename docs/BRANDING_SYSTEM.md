# Alpine Analytics Branding System

Complete branding system for Alpine Analytics LLC - neon on black theme with automated asset generation.

## 🎨 Brand Identity

### Color Palette

**Backgrounds (Black Scale)**
- Pure Black: `#000000`
- Primary: `#0a0a0f` (Main background)
- Secondary: `#0f0f1a` (Cards/surfaces)
- Tertiary: `#15151a` (Elevated surfaces)
- Border: `#1a1a2e` (Borders/dividers)

**Neon Accents**
- Cyan: `#18e0ff` (Primary accent)
- Pink: `#fe1c80` (Secondary accent)
- Purple: `#9600ff` (Tertiary accent)
- Orange: `#ff5f01` (Warning/accent)

**Semantic Colors**
- Success: `#00ff88` (Green)
- Error: `#ff2d55` (Red)
- Warning: `#ff5f01` (Orange)
- Info: `#18e0ff` (Cyan)

### Typography

- **Display**: Orbitron (Headlines - futuristic, tech)
- **Heading**: Montserrat (Section headers - modern, clean)
- **Body**: Inter (Body text - readable, professional)
- **Mono**: JetBrains Mono (Code/data - technical)

## 📁 File Structure

```
alpine-frontend/
├── lib/
│   └── brand.ts                    # Centralized brand configuration
├── app/
│   └── brand-variables.css         # CSS variables (auto-generated)
└── tailwind.config.ts              # Tailwind config with brand colors

scripts/
├── canva_oauth2.py                 # Canva OAuth 2.0 client
├── canva_brand_automation.py       # Brand automation
├── generate-brand-assets.js        # Asset generator
├── generate-pdf-branded.sh         # Branded PDF generator
├── pdf-template-alpine.tex         # LaTeX template with branding
└── alpine-brand-colors.tex         # LaTeX color definitions

brand-config.json                   # JSON export for external tools
```

## 🚀 Usage

### Web (Frontend)

```typescript
import { AlpineBrand, brandColors } from '@/lib/brand';

// Use brand colors
const primaryColor = AlpineBrand.colors.neon.cyan;
const backgroundColor = AlpineBrand.colors.black.primary;

// Use in Tailwind
<div className="bg-alpine-black-primary text-alpine-neon-cyan">
  Alpine Analytics
</div>
```

### PDF Generation

```bash
# Generate branded PDFs
./scripts/generate-pdf-branded.sh
```

### Canva Automation

```bash
# Generate social media post
cd scripts
source venv/bin/activate
python3 canva_brand_automation.py \
    --generate-social <TEMPLATE_ID> \
    --title "Alpine Analytics - New Signal Release" \
    --description "Check out our latest trading signals"
```

### Brand Assets

```bash
# Generate CSS variables, JSON, and LaTeX colors
node scripts/generate-brand-assets.js
```

## 🎯 Brand Guidelines

### Logo Usage

- **Primary Logo**: Use on dark backgrounds
- **Light Logo**: Use on light backgrounds (if needed)
- **Icon**: Use for favicons, app icons
- **Wordmark**: Use when space is limited

### Color Usage

- **Primary Accent (Cyan)**: Main CTAs, links, highlights
- **Secondary Accent (Pink)**: Secondary actions, accents
- **Tertiary Accent (Purple)**: Special features, premium content
- **Orange**: Warnings, alerts, important notices

### Typography

- **Display Font (Orbitron)**: Use for hero headlines, major titles
- **Heading Font (Montserrat)**: Use for section headers, subheadings
- **Body Font (Inter)**: Use for all body text, descriptions
- **Mono Font (JetBrains Mono)**: Use for code, data, technical content

## 🔧 Configuration

### Update Brand Colors

Edit `alpine-frontend/lib/brand.ts` and run:

```bash
node scripts/generate-brand-assets.js
```

This will update:
- CSS variables
- JSON config
- LaTeX colors
- Tailwind config (if needed)

### Add New Colors

1. Add to `AlpineBrand.colors` in `brand.ts`
2. Run asset generator
3. Update Tailwind config if needed

## 📦 Integration

### Canva API

Brand colors are automatically used in Canva automation:

```python
from canva_brand_automation import AlpineBrandAutomation

automation = AlpineBrandAutomation()
# Brand colors automatically included in autofill data
```

### PDF Generation

Branded LaTeX template automatically applies:
- Black background
- Neon accent colors
- Brand fonts
- Logo placement

### Web Components

All components should use brand colors from Tailwind:

```tsx
// Good
<div className="bg-alpine-black-primary text-alpine-neon-cyan">

// Bad
<div style={{ backgroundColor: '#0a0a0f' }}>
```

## 🎨 Design Principles

1. **Dark First**: Always design for dark backgrounds
2. **Neon Accents**: Use neon colors sparingly for maximum impact
3. **High Contrast**: Ensure text is always readable
4. **Consistent Spacing**: Use the spacing system
5. **Modern Tech Feel**: Clean, futuristic, professional

## 📚 Resources

- **Brand Config**: `alpine-frontend/lib/brand.ts`
- **Canva Setup**: `scripts/CANVA_SETUP.md`
- **Quick Start**: `scripts/QUICK_START_CANVA.md`
- **PDF Template**: `scripts/pdf-template-alpine.tex`

## 🔄 Updates

When updating the brand:

1. Edit `alpine-frontend/lib/brand.ts`
2. Run `node scripts/generate-brand-assets.js`
3. Update components to use new colors
4. Regenerate PDFs if needed
5. Update Canva templates if needed

## ✅ Checklist

- [x] Brand color palette defined
- [x] Typography system established
- [x] CSS variables generated
- [x] Tailwind config updated
- [x] PDF template created
- [x] Canva automation integrated
- [x] Asset generator created
- [ ] Logo files created (SVG)
- [ ] Brand guidelines document finalized
- [ ] All components updated to use brand system

