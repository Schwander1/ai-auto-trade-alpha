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
./commands/deploy all to production    # Deploy all services (recommended)
./commands/deploy argo to production   # Deploy Argo only
./commands/deploy alpine to production # Deploy Alpine only
```

## 📦 Packages

- **packages/argo-trading/** - Trading engine (Python/FastAPI)
- **packages/alpine-backend/** - User/subscription API (Python/FastAPI)
- **packages/alpine-frontend/** - Web dashboard (Next.js)
**✅ REMOVED:** `packages/shared/` has been removed per Rule 10 (Entity Separation). Each entity now has its own utilities.

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

**See:** [commands/README.md](commands/README.md) for complete command reference

### Production Deployment (Recommended)

**Agentic Deployment (Automated - Recommended):**
```bash
# Automated deployment with all 11 safety gates
pnpm agentic:deploy:auto argo production
pnpm agentic:deploy:auto alpine production

# Or use direct script
./scripts/agentic/automated-deployment.sh argo production
```

**Traditional Deployment:**
```bash
# Deploy all services to production
./commands/deploy all to production

# Deploy specific service
./commands/deploy argo to production
./commands/deploy alpine to production
```

**See:** `docs/AGENTIC_SETUP_GUIDE.md` for agentic features setup

### Health Checks
```bash
# Production health checks
./commands/health check all production
./commands/health check argo production

# Local health checks
./commands/health check all
```

### Status & Logs
```bash
# Check status
./commands/status check all production

# View logs
./commands/logs view all production
./commands/logs follow argo production
```

### Rollback
```bash
./commands/rollback argo production
./commands/rollback all production
```

### Agentic Features (AI-Powered Automation)

**Automated Workflows:**
```bash
# Automated deployment
pnpm agentic:deploy:auto argo production

# Automated troubleshooting
pnpm agentic:troubleshoot health_check
pnpm agentic:troubleshoot api_failure

# Weekly code quality review
pnpm agentic:code-review argo/argo/core

# Test coverage analysis
pnpm agentic:test-coverage argo/argo/core

# Monthly documentation update
pnpm agentic:docs-update

# Usage monitoring
pnpm agentic:usage
pnpm agentic:monitor
```

**See:** `docs/AGENTIC_QUICK_REFERENCE.md` for complete guide

### Local Development
```bash
# Start local services
./commands/start all

# Stop local services
./commands/stop all

# Restart services
./commands/restart all
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

### Cursor Pro Features

**Quick Access:**
- **Composer Mode:** `Cmd+I` - Multi-file refactoring across monorepo
- **Agent Mode:** `Cmd+Shift+A` - Autonomous task completion
- **Codebase Chat:** `Cmd+L` - Understand your entire codebase

**Automated Code Reviews:**
- **Bugbot:** Automatically reviews PRs for security, quality, and rule compliance
- Works through Cursor GitHub App (install from https://github.com/apps/cursor)
- Configure in Cursor dashboard settings
- Enforces all 25+ development rules

**See:** [docs/CURSOR_PRO_QUICK_REFERENCE.md](docs/CURSOR_PRO_QUICK_REFERENCE.md) for complete guide

**Profiles Strategy:**
- **Argo Trading Profile** - For `argo/` trading system work
- **Alpine Full-Stack Profile** - For `alpine-backend/` + `alpine-frontend/` work
- **Security-Sensitive Profile** - For IP/trade secret work
- **Monorepo Refactoring Profile** - For cross-service refactoring
- **Dev Workflow Profile** - For fast iteration

**See:** [docs/CURSOR_PROFILES_STRATEGY.md](docs/CURSOR_PROFILES_STRATEGY.md) for optimal profile configurations

## 📄 License

Private & Confidential
test
