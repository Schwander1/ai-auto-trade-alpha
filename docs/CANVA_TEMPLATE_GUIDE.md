# Canva Template Guide for Alpine Analytics

**Last Updated:** January 15, 2025

---

## Overview

This guide explains how to create and use Canva templates for Alpine Analytics branded social media assets, marketing materials, and reports.

---

## Brand Specifications for Canva Templates

### Color Palette

**Neon Accents:**
- **Cyan**: `#18e0ff` (Primary accent)
- **Pink**: `#fe1c80` (Secondary accent)
- **Purple**: `#9600ff` (Tertiary accent)
- **Orange**: `#ff5f01` (Warnings/CTAs)

**Backgrounds:**
- **Primary Black**: `#0a0a0f` (Main background)
- **Secondary Black**: `#0f0f1a` (Cards/surfaces)
- **Border**: `#1a1a2e` (Borders)

**Semantic:**
- **Success**: `#00ff88` (Profits/success)
- **Error**: `#ff2d55` (Losses/errors)

### Typography

- **Display/Headlines**: Orbitron (Bold/Black, 900 weight)
- **Headings**: Montserrat (Bold, 700 weight)
- **Body**: Inter (Regular/Medium, 400/500 weight)
- **Code/Data**: JetBrains Mono (Regular, 400 weight)

**Letter Spacing:**
- Orbitron: 0.15em (2-3px) for headlines

### Logo

- **Primary Logo**: Use `/brand/logo-primary.svg`
- **Icon**: Use `/brand/logo-icon.svg` for small spaces
- **Wordmark**: Use `/brand/logo-wordmark.svg` for text-only

**Logo Rules:**
- Always on dark backgrounds
- Minimum clear space = logo height
- Never distort or recolor

---

## Template Types

### 1. Social Media Posts

#### Instagram (1080x1080px)
- **Background**: `#0a0a0f` (primary black)
- **Headline**: Orbitron, 48-72px, neon cyan gradient
- **Body Text**: Inter, 18-24px, white
- **Accents**: Use neon colors sparingly (max 2 per post)
- **Logo**: Top-left or bottom-right, 40px height

#### Twitter (1200x675px)
- **Background**: `#0a0a0f`
- **Headline**: Orbitron, 36-48px, neon cyan
- **Body**: Inter, 16-20px, white
- **CTA Button**: Neon cyan background, black text
- **Logo**: Top-left, 32px height

#### LinkedIn (1200x627px)
- **Background**: `#0a0a0f`
- **Headline**: Montserrat Bold, 32-40px, neon cyan
- **Body**: Inter, 16-18px, white
- **Professional tone**: Less neon, more subtle
- **Logo**: Top-left, 36px height

### 2. Marketing Assets

#### Email Headers (600x200px)
- **Background**: `#0a0a0f`
- **Logo**: Left side, 50px height
- **Tagline**: "Adaptive AI Trading Signals" in Inter, 14px
- **Accent**: Thin neon cyan line at bottom

#### Banner Ads (728x90px)
- **Background**: `#0a0a0f`
- **Headline**: Orbitron, 24px, neon cyan
- **CTA**: Neon cyan button, "Learn More"
- **Logo**: Small icon, 24px

### 3. Report Covers

#### PDF Cover (8.5x11in / 2550x3300px)
- **Background**: `#0a0a0f`
- **Logo**: Top-center, 200px width
- **Title**: Orbitron, 72px, neon cyan gradient
- **Subtitle**: Montserrat, 24px, white
- **Date**: Inter, 14px, secondary text
- **Border**: Neon cyan line, 2px

---

## Creating Templates in Canva

### Step 1: Set Up Brand Colors

1. Open Canva
2. Go to **Brand Kit** (left sidebar)
3. Add colors:
   - Alpine Neon Cyan: `#18e0ff`
   - Alpine Neon Pink: `#fe1c80`
   - Alpine Neon Purple: `#9600ff`
   - Alpine Neon Orange: `#ff5f01`
   - Alpine Black Primary: `#0a0a0f`
   - Alpine Black Secondary: `#0f0f1a`
   - Alpine Success: `#00ff88`
   - Alpine Error: `#ff2d55`

### Step 2: Upload Brand Fonts

1. In **Brand Kit**, go to **Text styles**
2. Upload fonts (if available):
   - Orbitron (for headlines)
   - Montserrat (for headings)
   - Inter (for body)
   - JetBrains Mono (for code/data)

**Note:** If fonts aren't available, use similar system fonts:
- Orbitron → **Bebas Neue** or **Oswald** (bold, condensed)
- Montserrat → **Montserrat** (if available) or **Open Sans**
- Inter → **Inter** (if available) or **Roboto**

### Step 3: Upload Logo

1. In **Brand Kit**, go to **Logos**
2. Upload:
   - `logo-primary.svg`
   - `logo-icon.svg`
   - `logo-wordmark.svg`

### Step 4: Create Template

1. Create new design with correct dimensions
2. Set background to `#0a0a0f`
3. Add logo from Brand Kit
4. Create text styles:
   - **Display**: Orbitron/Bebas Neue, Bold, 48-72px, neon cyan
   - **Heading**: Montserrat/Open Sans, Bold, 24-36px, white
   - **Body**: Inter/Roboto, Regular, 16-18px, white
5. Add neon accents sparingly
6. Save as template

---

## Template Structure

### Standard Layout

```
┌─────────────────────────────────┐
│ [Logo]              [Optional]  │ ← Header (32px padding)
├─────────────────────────────────┤
│                                 │
│   [Headline - Orbitron]         │ ← Main content
│   [Body text - Inter]           │   (24-32px padding)
│   [CTA Button]                  │
│                                 │
├─────────────────────────────────┤
│ [Footer text]          [Date]   │ ← Footer (24px padding)
└─────────────────────────────────┘
```

### Design Principles

1. **Dark First**: Always use black backgrounds
2. **Neon Accents**: Maximum 2 neon colors per design
3. **Generous Spacing**: 24-32px padding preferred
4. **High Contrast**: White text on black
5. **Clear Hierarchy**: Use font sizes and weights to create hierarchy

---

## Using Templates with API

### Generate Social Media Post

```bash
cd scripts
source venv/bin/activate

python3 canva_brand_automation.py \
  --generate-social <TEMPLATE_ID> \
  --title "Alpine Analytics - New Signal Release" \
  --description "Check out our latest trading signals with 95%+ win rate" \
  --cta "Learn More"
```

### Template Variables

When creating templates, use these variable names for autofill:

- `{{title}}` - Main headline
- `{{description}}` - Body text
- `{{cta}}` - Call-to-action text
- `{{date}}` - Current date
- `{{brand_colors.primary}}` - Neon cyan
- `{{brand_colors.secondary}}` - Neon pink

---

## Template Checklist

Before saving a template:

- [ ] Background is `#0a0a0f` (primary black)
- [ ] Logo is from Brand Kit
- [ ] Text uses brand fonts (or similar)
- [ ] Maximum 2 neon colors used
- [ ] Spacing is 24-32px
- [ ] Text is readable (16px+ for body)
- [ ] Logo has clear space (logo height)
- [ ] Design follows brand guidelines

---

## Example Templates

### Social Media Post Template

**Layout:**
- Background: `#0a0a0f`
- Logo: Top-left, 40px
- Headline: Orbitron, 48px, neon cyan, centered
- Body: Inter, 18px, white, centered
- CTA Button: Neon cyan, black text, centered
- Footer: "Alpine Analytics®" in Inter, 12px, secondary text

**Colors Used:**
- Primary: Neon cyan
- Background: Primary black
- Text: White

### Report Cover Template

**Layout:**
- Background: `#0a0a0f`
- Logo: Top-center, 200px
- Title: Orbitron, 72px, neon cyan gradient, centered
- Subtitle: Montserrat, 24px, white, centered
- Date: Inter, 14px, secondary text, bottom-right
- Border: Neon cyan line, 2px, bottom

**Colors Used:**
- Primary: Neon cyan
- Background: Primary black
- Text: White, secondary text

---

## Automation Script

The `canva_brand_automation.py` script automatically applies brand colors:

```python
from canva_brand_automation import AlpineBrandAutomation

automation = AlpineBrandAutomation()

# Generate social media post
result = automation.generate_social_post(
    template_id="YOUR_TEMPLATE_ID",
    title="Alpine Analytics - New Signal",
    description="95%+ win rate trading signals",
    cta="Start Trading"
)
```

---

## Best Practices

1. **Consistency**: Use the same template structure across all assets
2. **Simplicity**: Don't overcrowd designs
3. **Readability**: Ensure text is always readable
4. **Brand Colors**: Stick to the brand palette
5. **Spacing**: Use generous spacing (24-32px)
6. **Logo**: Always use logo from Brand Kit
7. **Typography**: Use brand fonts or close alternatives

---

## Troubleshooting

**Issue:** Fonts not available in Canva
- **Solution:** Use similar system fonts (see Step 2)

**Issue:** Colors don't match
- **Solution:** Use exact hex codes from brand palette

**Issue:** Logo looks distorted
- **Solution:** Maintain aspect ratio, use clear space

**Issue:** Template doesn't work with API
- **Solution:** Ensure variable names match (`{{title}}`, etc.)

---

## Resources

- **Brand Config**: `alpine-frontend/lib/brand.ts`
- **Brand Rules**: `Rules/35_BRANDING.md`
- **Canva Setup**: `scripts/CANVA_SETUP.md`
- **API Script**: `scripts/canva_brand_automation.py`

---

**Template Creation Complete!** 🎨

Your Canva templates are now ready for automated brand asset generation.

