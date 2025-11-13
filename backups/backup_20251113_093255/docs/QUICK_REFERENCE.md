# Documentation Quick Reference

## 📋 Common Commands

### Generate PDFs
```bash
# Generate all PDFs
./scripts/generate-pdf.sh

# Generate specific set
pandoc docs/InvestorDocs/v1.0_*.md -o pdfs/InvestorDocs_v1.0_$(date +%Y-%m-%d).pdf \
  --pdf-engine=xelatex --toc --toc-depth=3 \
  --variable=geometry:margin=2cm \
  --variable=fontsize:12pt \
  --variable=linestretch:1.5 \
  --variable=mainfont:Georgia \
  --variable=sansfont:"DejaVu Sans" \
  --variable=monofont:"DejaVu Sans Mono" \
  --variable=linkcolor:#0066CC \
  --variable=urlcolor:#0066CC
```

### Verify Standards
```bash
./scripts/verify-docs.sh
```

### Standardize New Files
```bash
python3 scripts/standardize-docs.py
```

## 📁 File Locations

- **InvestorDocs**: `docs/InvestorDocs/v1.0_*.md`
- **TechnicalDocs**: `docs/TechnicalDocs/v1.0_*.md`
- **SystemDocs**: `docs/SystemDocs/v1.0_*.md`
- **PDFs**: `pdfs/*.pdf`

## 🎯 Versioning Rules

- Format: `v[VERSION]_[SEQUENCE]_[DESCRIPTION].md`
- Example: `v1.0_01_executive_summary.md`
- Update version for major changes: `v1.1_01_*.md`

## ✨ Formatting Checklist

- [ ] Code blocks have language: ` ```python `
- [ ] H1 only in first file, H2 in others
- [ ] Proper spacing (one blank line between sections)
- [ ] Frontmatter in first file only
- [ ] Version number in filename matches frontmatter

## 📞 Need Help?

See `docs/DOCUMENTATION_ORGANIZATION.md` for complete details.

