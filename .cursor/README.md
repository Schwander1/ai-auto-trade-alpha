# Cursor Configuration

This directory contains Cursor-specific settings and configurations optimized for the Argo-Alpine monorepo workspace.

## Files

### `settings.json`
Cursor-specific settings including:
- Codebase indexing configuration
- Composer and Agent settings
- Auto-loading rules from `.cursorrules/` and `Rules/`
- Language-specific formatters and settings
- Performance optimizations

## Configuration Overview

### Indexing Optimization
The settings exclude large directories from indexing to improve performance:
- `node_modules/`, `venv/`, `__pycache__/`
- `dist/`, `build/`, `.next/`, `out/`
- `archive/`, `backups/`, `logs/`
- Large data files and lock files

### Entity Separation
Settings respect the separation between:
- **Argo Capital** (`argo/`)
- **Alpine Analytics LLC** (`alpine-backend/` + `alpine-frontend/`)

### Language Support
Optimized for:
- **Python 3.11+** (FastAPI, type hints, Black formatter)
- **TypeScript** (strict mode, Next.js 14, React 18)
- **JavaScript/JSX** (ESLint, Prettier)
- **Markdown** (documentation)
- **YAML** (Docker Compose, CI/CD)
- **SQL** (database migrations)

## Rules Integration

Cursor automatically loads rules from:
1. `.cursorrules/**/*.mdc` - Cursor-specific rules
2. `Rules/**/*.md` - Comprehensive project rules

## Performance

### Indexing Exclusions
See `.cursorignore` for complete list of excluded patterns.

### Recommended Extensions
See `.vscode/extensions.json` for recommended VS Code/Cursor extensions.

## Maintenance

### Updating Settings
1. Edit `.cursor/settings.json`
2. Cursor will reload settings automatically
3. Restart Cursor if changes don't apply

### Adding New Exclusions
1. Add pattern to `.cursorignore`
2. Add pattern to `.cursor/settings.json` → `cursor.codebase.indexing.excludePatterns`
3. Rebuild codebase index if needed

## Related Files

- `.cursorrules/` - Cursor rules directory
- `.cursorignore` - Indexing exclusions
- `.vscode/settings.json` - Workspace editor settings
- `.vscode/extensions.json` - Recommended extensions
- `.editorconfig` - Editor configuration

## Notes

- Settings are optimized for macOS (zsh terminal)
- Python interpreter defaults to `alpine-backend/venv/bin/python`
- Format-on-save is enabled for all supported languages
- Auto-imports and organize imports are enabled
