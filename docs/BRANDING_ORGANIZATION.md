# Branding System Organization

**Last Updated:** January 15, 2025

---

## File Structure

```
argo-alpine-workspace/
├── alpine-frontend/
│   ├── lib/
│   │   └── brand.ts                    # ⭐ SINGLE SOURCE OF TRUTH
│   ├── app/
│   │   ├── globals.css                 # Global styles with brand CSS
│   │   └── brand-variables.css         # Auto-generated CSS variables
│   ├── public/
│   │   └── brand/                      # Logo files
│   │       ├── logo-primary.svg
│   │       ├── logo-icon.svg
│   │       ├── logo-wordmark.svg
│   │       ├── logo-light.svg
│   │       └── logo-dark.svg
│   └── tailwind.config.ts              # Tailwind with brand colors
│
├── scripts/
│   ├── canva_oauth2.py                 # Canva OAuth client
│   ├── canva_brand_automation.py       # Canva automation
│   ├── generate-brand-assets.js        # Asset generator
│   ├── pdf-template-alpine.tex         # PDF LaTeX template
│   ├── alpine-brand-colors.tex         # Auto-generated LaTeX colors
│   ├── CANVA_SETUP.md                  # Canva setup guide
│   └── requirements.txt                # Python dependencies
│
├── docs/
│   ├── BRANDING_SYSTEM.md              # Main branding docs
│   ├── BRAND_STYLE_GUIDE_COMPLETE.md   # Complete style guide
│   ├── BRAND_QUICK_REFERENCE.md        # Quick reference
│   ├── BRANDING_SETUP_WALKTHROUGH.md   # Setup walkthrough
│   └── BRANDING_ORGANIZATION.md        # This file
│
├── Rules/
│   └── 35_BRANDING.md                  # Branding rules
│
└── brand-config.json                   # Auto-generated JSON export
```

---

## Single Source of Truth

**`alpine-frontend/lib/brand.ts`** is the SINGLE SOURCE OF TRUTH for all brand configuration.

### What It Contains
- Color palettes (black, neon, semantic, text)
- Typography system (fonts, sizes, weights, letter spacing)
- Spacing system
- Effects (glow, shadow, pulse)
- Logo paths
- Metadata

### How It's Used
1. **Frontend:** Imported directly in components
2. **Tailwind:** Referenced in `tailwind.config.ts`
3. **CSS:** Generated to `brand-variables.css`
4. **PDF:** Colors exported to LaTeX
5. **Canva:** JSON export used in automation
6. **External Tools:** JSON export for other systems

### Update Process
1. Edit `alpine-frontend/lib/brand.ts`
2. Run `node scripts/generate-brand-assets.js`
3. All assets automatically updated

---

## Asset Generation Flow

```
brand.ts (Source)
    │
    ├─→ generate-brand-assets.js
    │       │
    │       ├─→ brand-variables.css (CSS variables)
    │       ├─→ brand-config.json (JSON export)
    │       └─→ alpine-brand-colors.tex (LaTeX colors)
    │
    ├─→ tailwind.config.ts (Direct import)
    │
    └─→ Components (Direct import)
```

**Rule:** Never edit generated files directly. Always edit `brand.ts` and regenerate.

---

## Logo Organization

### Location
`alpine-frontend/public/brand/`

### Files
- `logo-primary.svg` - Full logo (main)
- `logo-icon.svg` - Icon only (64x64px)
- `logo-wordmark.svg` - Text only
- `logo-light.svg` - White version (if needed)
- `logo-dark.svg` - Black version (if needed)

### Usage
- **Web:** `/brand/logo-primary.svg`
- **PDF:** Convert to PDF or use SVG
- **Canva:** Upload as assets

### Rules
- Never modify logo colors
- Maintain aspect ratio
- Use clear space (logo height)
- Include trademark (®) in formal docs

---

## Documentation Organization

### Rules
- **Location:** `Rules/35_BRANDING.md`
- **Purpose:** Mandatory branding standards
- **Audience:** All developers/designers

### Guides
- **Setup:** `docs/BRANDING_SETUP_WALKTHROUGH.md`
- **Style Guide:** `docs/BRAND_STYLE_GUIDE_COMPLETE.md`
- **Quick Reference:** `docs/BRAND_QUICK_REFERENCE.md`
- **Organization:** `docs/BRANDING_ORGANIZATION.md` (this file)

### Integration Docs
- **Canva:** `scripts/CANVA_SETUP.md`
- **PDF:** `scripts/pdf-template-alpine.tex` (comments)
- **Frontend:** `Rules/11_FRONTEND.md` (branding section)

---

## Version Control

### What to Version
- ✅ `brand.ts` (source of truth)
- ✅ Logo SVG files
- ✅ Documentation
- ✅ Templates (LaTeX, Canva)
- ✅ Scripts

### What NOT to Version
- ❌ Generated files (`brand-variables.css`, `brand-config.json`)
- ❌ Build artifacts
- ❌ Temporary files

### Gitignore
```
# Generated brand assets
alpine-frontend/app/brand-variables.css
brand-config.json
scripts/alpine-brand-colors.tex
```

**Note:** These are generated, so they can be regenerated from `brand.ts`.

---

## Naming Conventions

### Files
- **Config:** `brand.ts` (lowercase, descriptive)
- **Logos:** `logo-{variant}.svg` (kebab-case)
- **Docs:** `BRANDING_{TOPIC}.md` (UPPERCASE, descriptive)
- **Scripts:** `{purpose}-{tool}.{ext}` (kebab-case)

### Code
- **Constants:** `AlpineBrand` (PascalCase)
- **Colors:** `alpine-neon-cyan` (kebab-case in Tailwind)
- **CSS Classes:** `glow-cyan` (kebab-case)
- **Functions:** `generateBrandAssets` (camelCase)

---

## Integration Points

### Frontend (Next.js)
- **Config:** `lib/brand.ts`
- **Styles:** `app/globals.css`
- **Tailwind:** `tailwind.config.ts`
- **Components:** Import from `@/lib/brand`

### PDF Generation
- **Template:** `scripts/pdf-template-alpine.tex`
- **Colors:** `scripts/alpine-brand-colors.tex` (generated)
- **Command:** `pandoc --template=scripts/pdf-template-alpine.tex`

### Canva Automation
- **OAuth:** `scripts/canva_oauth2.py`
- **Automation:** `scripts/canva_brand_automation.py`
- **Config:** Uses `brand-config.json` (generated)

### External Tools
- **JSON Export:** `brand-config.json`
- **Format:** Standard JSON
- **Usage:** Import into any system

---

## Maintenance Workflow

### Regular Updates
1. Edit `alpine-frontend/lib/brand.ts`
2. Run `node scripts/generate-brand-assets.js`
3. Test in frontend
4. Update components if needed
5. Regenerate PDFs
6. Update Canva templates
7. Document changes

### Major Updates
1. Plan changes
2. Update `brand.ts`
3. Regenerate all assets
4. Update all components
5. Test thoroughly
6. Update documentation
7. Version bump

---

## Quality Assurance

### Checklist
- [ ] All colors from `brand.ts`
- [ ] Typography follows hierarchy
- [ ] Logo used correctly
- [ ] Spacing uses scale
- [ ] Contrast meets standards
- [ ] Animations are subtle
- [ ] Mobile responsive
- [ ] Accessibility tested

### Automated Checks
- Linting for brand color usage
- Type checking for brand config
- CSS variable validation
- Logo file verification

---

## Support & Resources

### Documentation
- Setup: `docs/BRANDING_SETUP_WALKTHROUGH.md`
- Rules: `Rules/35_BRANDING.md`
- Style Guide: `docs/BRAND_STYLE_GUIDE_COMPLETE.md`

### Tools
- Asset Generator: `scripts/generate-brand-assets.js`
- Canva Client: `scripts/canva_oauth2.py`
- PDF Template: `scripts/pdf-template-alpine.tex`

### Contact
- Issues: Check troubleshooting in walkthrough
- Updates: Follow maintenance workflow
- Questions: Review documentation first

---

**Organization Complete!** 🎨

All brand assets are organized, documented, and ready for use.

