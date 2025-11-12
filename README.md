# Argo → Alpine Monorepo

Intelligent, self-optimizing trading signal platform with automated CI/CD, monitoring, and continuous improvement.

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install

# Start all services
pnpm dev

# Run tests
pnpm test

# Deploy to production
pnpm deploy:argo    # Deploy Argo to 178.156.194.174
pnpm deploy:alpine  # Deploy Alpine to 91.98.153.49
```

## 📦 Packages

- **packages/argo-trading/** - Trading engine (Python/FastAPI)
- **packages/alpine-backend/** - User/subscription API (Python/FastAPI)
- **packages/alpine-frontend/** - Web dashboard (Next.js)
- **packages/shared/** - Shared utilities (TypeScript + Python)

## 🛠️ Development

```bash
# Start development servers
pnpm dev

# Run linting
pnpm lint

# Run type checking
pnpm type-check

# Format code
pnpm format
```

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Run with coverage
pnpm test -- --coverage

# Run specific package tests
cd packages/argo-trading && pytest
cd packages/alpine-frontend && pnpm test
```

## 🚢 Deployment

### Argo (178.156.194.174)
```bash
pnpm deploy:argo
```

### Alpine (91.98.153.49)
```bash
pnpm deploy:alpine
```

### Health Checks
```bash
pnpm health
```

### Rollback
```bash
pnpm rollback
```

## 📊 Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Argo Metrics: http://localhost:8000/metrics

## 🔧 Configuration

- `turbo.json` - Build pipeline configuration
- `.cursorrules` - AI optimization rules
- `.github/workflows/` - CI/CD pipelines
- `scripts/` - Deployment and utility scripts

## 📝 Versioning

This project uses [Semantic Versioning](https://semver.org/) with automated changelog generation.

## 🤖 AI Optimization

The `.cursorrules` file enables Cursor to:
- Automatically suggest performance improvements
- Flag security vulnerabilities
- Recommend test cases
- Optimize database queries
- Suggest caching opportunities
- Identify refactoring needs

## 📄 License

Private & Confidential
