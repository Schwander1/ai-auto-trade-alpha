# Developer Onboarding Guide

**Welcome to the Argo → Alpine Monorepo!** This guide will help you get set up and productive quickly.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Development Workflow](#development-workflow)
4. [Project Structure](#project-structure)
5. [Testing](#testing)
6. [Code Review Process](#code-review-process)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Node.js**: v18.x or v20.x ([Download](https://nodejs.org/))
- **pnpm**: v8.x or higher (`npm install -g pnpm@8`)
- **Python**: 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker**: Latest version ([Download](https://www.docker.com/get-started))
- **Git**: Latest version
- **PostgreSQL**: 14+ (or use Docker)
- **Redis**: 6+ (or use Docker)

### Recommended Tools

- **VS Code** with extensions:
  - Python
  - ESLint
  - Prettier
  - Docker
- **Postman** or **Insomnia** for API testing
- **DBeaver** or **pgAdmin** for database management

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd argo-alpine-workspace
```

### 2. Install Dependencies

```bash
# Install monorepo dependencies
pnpm install

# Install Python dependencies (if needed)
cd argo && pip install -r requirements.txt
cd ../alpine-backend && pip install -r requirements.txt
```

### 3. Environment Setup

#### Copy Environment Files

```bash
# Argo
cp argo/.env.example argo/.env

# Alpine Backend
cp alpine-backend/.env.example alpine-backend/.env

# Alpine Frontend
cp alpine-frontend/.env.example alpine-frontend/.env.local
```

#### Configure Environment Variables

**Argo (`argo/.env`):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/argo
REDIS_URL=redis://localhost:6379/0
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
```

**Alpine Backend (`alpine-backend/.env`):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/alpine
REDIS_URL=redis://localhost:6379/1
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:3000
```

**Alpine Frontend (`alpine-frontend/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 4. Start Services with Docker Compose

```bash
# Start all services (PostgreSQL, Redis, etc.)
docker-compose up -d

# Or start individual services
docker-compose up -d postgres redis
```

### 5. Initialize Database

```bash
# Run migrations
cd alpine-backend
alembic upgrade head

# Or for Argo
cd argo
python -m alembic upgrade head
```

### 6. Start Development Servers

```bash
# Start all services
pnpm dev

# Or start individually:
# Argo
cd argo && python -m uvicorn main:app --reload --port 8000

# Alpine Backend
cd alpine-backend && python -m uvicorn backend.main:app --reload --port 8001

# Alpine Frontend
cd alpine-frontend && pnpm dev
```

### 7. Verify Setup

```bash
# Check health endpoints
curl http://localhost:8000/api/v1/health  # Argo
curl http://localhost:8001/health         # Alpine Backend
curl http://localhost:3000/api/health     # Alpine Frontend
```

---

## Development Workflow

### Branch Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch
- **Feature branches**: `feature/description`
- **Bug fixes**: `fix/description`
- **Hotfixes**: `hotfix/description`

### Creating a Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Run tests
pnpm test

# 4. Run linting
pnpm lint

# 5. Commit changes
git add .
git commit -m "feat: add my feature"

# 6. Push and create PR
git push origin feature/my-feature
```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(auth): add OAuth2 login
fix(api): resolve rate limiting issue
docs(readme): update setup instructions
```

---

## Project Structure

```
argo-alpine-workspace/
├── argo/                    # Trading engine (Python/FastAPI)
│   ├── argo/
│   │   ├── core/           # Core trading logic
│   │   ├── integrations/   # External integrations
│   │   └── compliance/     # Compliance features
│   ├── tests/              # Tests
│   └── main.py             # FastAPI app
│
├── alpine-backend/          # User/subscription API (Python/FastAPI)
│   ├── backend/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core utilities
│   │   ├── models/         # Database models
│   │   └── auth/           # Authentication
│   └── tests/              # Tests
│
├── alpine-frontend/         # Web dashboard (Next.js)
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── __tests__/          # Tests
│
├── packages/                # Shared packages
│   └── shared/             # Shared utilities
│
├── scripts/                 # Deployment and utility scripts
├── docs/                    # Documentation
└── Rules/                   # Development rules
```

---

## Testing

### Running Tests

```bash
# All tests
pnpm test

# Specific package
pnpm --filter alpine-frontend test

# With coverage
pnpm test -- --coverage

# Watch mode
pnpm test:watch
```

### Python Tests

```bash
# Argo tests
cd argo && pytest

# Alpine Backend tests
cd alpine-backend && pytest

# With coverage
pytest --cov=backend --cov-report=html
```

### Test Coverage Requirements

- **Critical paths**: 95%+ coverage
- **Overall codebase**: 80%+ coverage
- **New code**: 100% coverage required

---

## Code Review Process

### Before Submitting PR

- [ ] All tests pass
- [ ] Code is linted (`pnpm lint`)
- [ ] Type checking passes (`pnpm type-check`)
- [ ] Documentation updated
- [ ] No console.log or debugger statements
- [ ] No hardcoded secrets or credentials

### PR Checklist

1. **Description**: Clear description of changes
2. **Tests**: Tests added/updated
3. **Documentation**: Docs updated if needed
4. **Breaking Changes**: Documented if any
5. **Security**: Security implications considered

### Review Guidelines

- Be constructive and respectful
- Focus on code quality, not personal preferences
- Ask questions if something is unclear
- Approve when ready, request changes if needed

---

## Common Tasks

### Adding a New API Endpoint

1. **Create endpoint** in `backend/api/`:
```python
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/my-endpoint", tags=["my-tag"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello"}
```

2. **Register router** in `backend/main.py`:
```python
app.include_router(router)
```

3. **Add tests** in `tests/`:
```python
def test_my_endpoint(client):
    response = client.get("/api/v1/my-endpoint/")
    assert response.status_code == 200
```

4. **Update OpenAPI docs** (auto-generated by FastAPI)

### Adding a New Frontend Component

1. **Create component** in `alpine-frontend/components/`:
```tsx
export function MyComponent() {
  return <div>Hello</div>
}
```

2. **Add tests** in `alpine-frontend/__tests__/`:
```tsx
import { render } from '@testing-library/react'
import { MyComponent } from '../components/MyComponent'

test('renders correctly', () => {
  render(<MyComponent />)
})
```

### Database Migrations

```bash
# Create migration
cd alpine-backend
alembic revision --autogenerate -m "description"

# Review migration file
# Edit if needed

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Deploying to Production

See [DEPLOYMENT_INSTRUCTIONS.md](../DEPLOYMENT_INSTRUCTIONS.md) for detailed deployment procedures.

**Quick deploy:**
```bash
./commands/deploy alpine to production
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

#### Redis Connection Errors

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

#### Dependency Issues

```bash
# Clear and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install

# For Python
pip install --upgrade -r requirements.txt
```

#### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/test_specific.py::test_function

# Debug with pdb
pytest --pdb
```

---

## Getting Help

### Resources

- **Documentation**: `/docs` directory
- **Rules**: `/Rules` directory
- **API Docs**: http://localhost:8001/api/v1/docs
- **System Architecture**: `docs/SystemDocs/COMPLETE_SYSTEM_ARCHITECTURE.md`

### Questions?

- Check existing documentation first
- Search for similar issues in codebase
- Ask in team chat/Slack
- Create an issue if it's a bug

---

## Next Steps

1. ✅ Complete setup
2. ✅ Read [Development Rules](../Rules/README.md)
3. ✅ Review [API Design Rules](../Rules/26_API_DESIGN.md)
4. ✅ Check [Security Rules](../Rules/07_SECURITY.md)
5. ✅ Start coding!

**Welcome aboard! 🚀**
