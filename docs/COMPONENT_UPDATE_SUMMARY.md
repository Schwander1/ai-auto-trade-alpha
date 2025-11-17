# Component Update Summary

**Date:** January 15, 2025

## Status

Components are being updated to use the Alpine brand system. A script has been created to automate the process.

## Color Mappings

Old → New:
- `electric-cyan` → `alpine-neon-cyan`
- `neon-pink` → `alpine-neon-pink`
- `neon-purple` → `alpine-neon-purple`
- `laser-green` → `alpine-semantic-success`
- `warning-red` → `alpine-semantic-error`
- `ice-blue` → `alpine-text-primary`
- `space-gray` → `alpine-black-primary`
- `black` → `alpine-black-primary`

## Components Updated

- ✅ `WhatToExpect.tsx` - Updated to use brand colors and classes

## Components Pending Update

The following components need to be updated (script available):
- `HighConfidenceSignals.tsx`
- `Solution.tsx`
- `OurEdge.tsx`
- `Hero.tsx`
- `Header.tsx`
- And 15+ more components

## Update Script

Run the update script:
```bash
cd scripts
./update-components-to-brand.sh
```

This will:
1. Find all `.tsx` and `.ts` files in components
2. Replace old color names with new brand colors
3. Create backups (`.bak` files)
4. Update text, background, and border color classes

## Manual Review Required

After running the script:
1. Review changes in each file
2. Test components in browser
3. Remove `.bak` files when satisfied
4. Commit changes

## Next Steps

1. Run update script
2. Test frontend: `cd alpine-frontend && npm run dev`
3. Review each component visually
4. Fix any issues manually
5. Remove backup files
6. Commit changes

