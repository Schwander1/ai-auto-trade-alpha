# Documentation System

Professional, organized documentation with intelligent PDF generation.

## 📁 Document Sets

### InvestorDocs
Investor and acquisition documentation (7 files)
- Location: `docs/InvestorDocs/`
- PDF: `pdfs/InvestorDocs_v1.0_YYYY-MM-DD.pdf`

### TechnicalDocs
Technical and system documentation (6 files)
- Location: `docs/TechnicalDocs/`
- PDF: `pdfs/TechnicalDocs_v1.0_YYYY-MM-DD.pdf`

### SystemDocs
General system and setup documentation (4 files)
- Location: `docs/SystemDocs/`
- PDF: `pdfs/SystemDocs_v1.0_YYYY-MM-DD.pdf`

## 🚀 Quick Start

### Generate All PDFs

```bash
./scripts/generate-pdf.sh
```

### Generate Specific PDF

```bash
# InvestorDocs
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

## 📋 Versioning

**Format:** `v[VERSION]_[SEQUENCE]_[DESCRIPTION].md`

- **VERSION**: Semantic versioning (v1.0, v1.1, v2.0)
- **SEQUENCE**: Two-digit ordering (01, 02, 03...)
- **DESCRIPTION**: Snake_case, lowercase

## ✨ Formatting Standards

- **Body Text**: Georgia 12pt, 1.5x line spacing
- **Headings**: DejaVu Sans Bold (H1=24pt, H2=16pt, H3=14pt)
- **Code Blocks**: DejaVu Sans Mono 11pt, language required
- **Layout**: A4, 2cm margins, left-aligned
- **Colors**: Links #0066CC, high contrast

## 📝 Adding New Files

1. Follow versioning scheme: `v1.0_08_new_file.md`
2. Use H2 headings (H1 only in first file)
3. Include language in all code blocks: ` ```python `
4. Maintain spacing standards
5. Run verification: `./scripts/verify-docs.sh`

## 🔄 Updating Versions

When making significant changes:

1. Update version number (v1.0 → v1.1)
2. Rename files: `v1.1_01_*.md`
3. Update frontmatter version
4. Regenerate PDFs

---

For detailed information, see `docs/DOCUMENTATION_ORGANIZATION.md`

