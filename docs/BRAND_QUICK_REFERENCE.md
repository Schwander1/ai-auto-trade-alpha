# Alpine Analytics - Brand Quick Reference

## Colors (Hex Codes)

**Neon Accents:**
- Cyan: `#18e0ff`
- Pink: `#fe1c80`
- Purple: `#9600ff`
- Orange: `#ff5f01`

**Backgrounds:**
- Primary: `#0a0a0f`
- Secondary: `#0f0f1a`
- Border: `#1a1a2e`

**Semantic:**
- Success: `#00ff88`
- Error: `#ff2d55`

## Fonts

- Display: Orbitron (headlines)
- Heading: Montserrat (sections)
- Body: Inter (text)
- Mono: JetBrains Mono (code)

## Tailwind Classes

```tsx
bg-alpine-black-primary
text-alpine-neon-cyan
border-alpine-neon-pink
glow-cyan
pulse-neon
```

## Canva API

```bash
# List designs
python3 scripts/canva_oauth2.py --list-designs

# Generate asset
python3 scripts/canva_brand_automation.py --generate-social <ID> --title "..." --description "..."
```

## PDF Generation

```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  --template=scripts/pdf-template-alpine.tex
```

## Brand Config

```typescript
import { AlpineBrand } from '@/lib/brand';
const color = AlpineBrand.colors.neon.cyan;
```

## Quick Rules

- ✅ Dark backgrounds only
- ✅ 16px minimum body text
- ✅ 0.15em letter-spacing for Orbitron
- ✅ Maximum 2 neon colors per component
- ✅ 24-32px spacing preferred
- ❌ No light backgrounds
- ❌ No text < 15px
- ❌ No logo distortion

