# Complete System Architecture Documentation

**Date:** January 15, 2025  
**Version:** 4.0  
**Status:** Complete System Overview

---

## Executive Summary

This document provides a comprehensive, front-to-end overview of the workspace architecture, covering all components, data flows, and operational procedures.

**CRITICAL:** This workspace contains **TWO COMPLETELY SEPARATE AND INDEPENDENT ENTITIES**:
- **Argo Capital** - Independent Trading Company
- **Alpine Analytics LLC** - Independent Analytics Company

These entities share **NO code, NO dependencies, and NO relationships**. They exist in the same workspace for development convenience only.

---

## System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKSPACE STRUCTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   ARGO CAPITAL   │         │ ALPINE ANALYTICS │            │
│  │  (INDEPENDENT)   │         │  LLC (INDEPENDENT)│            │
│  │                  │         │                  │            │
│  │  Signal Gen      │         │  Signal Dist     │            │
│  │  Trading Engine  │         │  User Dashboard  │            │
│  │                  │         │                  │            │
│  └──────────────────┘         └──────────────────┘            │
│         │                              │                        │
│         │ (API Integration Only)       │                        │
│         │                              │                        │
│         ▼                              ▼                        │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │  Paper Trading   │         │   PostgreSQL     │            │
│  │  (Alpaca API)    │         │   (Signals DB)   │            │
│  └──────────────────┘         └──────────────────┘            │
│                                                                 │
│  NO SHARED CODE | NO CROSS-REFERENCES | SEPARATE ENTITIES      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entity Separation (CRITICAL)

### Argo Capital
- **Entity:** Argo Capital (Independent Trading Company)
- **Location:** `argo/`
- **Type:** Trading Engine (Python/FastAPI)
- **Purpose:** Proprietary trading system
- **Deployment:** Independent
- **Code:** Completely separate, no shared code
- **Dependencies:** NO dependencies on Alpine Analytics
- **IP:** Argo-specific algorithms and methods

### Alpine Analytics LLC
- **Entity:** Alpine Analytics LLC (Independent Analytics Company)
- **Backend Location:** `alpine-backend/`
- **Frontend Location:** `alpine-frontend/`
- **Type:** Analytics Platform (Python/FastAPI + Next.js)
- **Purpose:** Signal distribution platform
- **Deployment:** Independent (backend + frontend coupled)
- **Code:** Completely separate, no shared code
- **Dependencies:** NO dependencies on Argo Capital
- **IP:** Alpine-specific algorithms and methods (e.g., Weighted Consensus v6.0)

### Integration (Business Relationship Only)

**External Signal Provider Integration:**
- Alpine Analytics receives signals from external signal provider via API
- **NO code dependencies** - pure API integration
- **NO shared code** - complete separation
- **NO cross-references** in code or documentation
- External provider sends signals → Alpine stores in its own database

**Note:** This is a business integration (Alpine is a customer of external signal provider), not a code dependency.

---

## Component Architecture

### 1. Argo Capital (Signal Generation & Trading)

**Location:** `argo/`

#### Core Components

1. **Signal Generation Service** (`argo/core/signal_generation_service.py`)
   - Generates signals every 5 seconds
   - Uses proprietary consensus algorithm
   - Integrates 4 data sources
   - Applies risk management
   - Executes trades (if enabled)

2. **Consensus Engine** (`argo/core/weighted_consensus_engine.py`)
   - Combines signals from multiple sources
   - Weighted voting algorithm
   - 75% consensus threshold
   - Configurable source weights

3. **Paper Trading Engine** (`argo/core/paper_trading_engine.py`)
   - Alpaca API integration
   - Environment-aware (dev/prod accounts)
   - Position management
   - Order execution
   - Risk management

4. **Data Sources**
   - Massive.com (40% weight)
   - Alpha Vantage (25% weight)
   - X Sentiment (20% weight)
   - Sonar AI (15% weight)

5. **Backtesting Framework** (`argo/backtest/`)
   - Strategy backtester (signal quality)
   - Profit backtester (trading profitability)
   - Walk-forward testing
   - Parameter optimization

#### Data Flow

```
Market Data → Data Sources → Consensus Engine → Signal Generation
    ↓
Risk Validation → Trade Execution → Position Management
    ↓
Performance Tracking → External API (if configured)
```

---

### 2. Alpine Analytics LLC (Signal Distribution)

**Location:** `alpine-backend/` + `alpine-frontend/`

#### Core Components

1. **Backend API** (`alpine-backend/backend/main.py`)
   - User authentication
   - Signal distribution
   - Subscription management
   - WebSocket real-time updates
   - External signal provider integration (API only)

2. **Frontend Dashboard** (`alpine-frontend/`)
   - Next.js application
   - Real-time signal display
   - User dashboard
   - Backtesting interface

3. **Database** (PostgreSQL)
   - User management
   - Signal storage
   - Subscription tracking
   - Audit logs

#### Data Flow

```
External Signal Provider (API) → Alpine Backend API
    ↓
PostgreSQL Storage → WebSocket Push
    ↓
Frontend Dashboard → User Notification
```

---

## Environment Setup

### Development Environment

- **Location:** Local machine
- **Argo Alpaca Account:** Dev paper trading account
- **Alpine Database:** SQLite (local) or PostgreSQL
- **Config:** `argo/config.json` (local)

### Production Environment

- **Argo Server:** 178.156.194.174
- **Alpine Server:** 91.98.153.49
- **Argo Alpaca Account:** Production paper trading account
- **Alpine Database:** PostgreSQL (production)
- **Config:** AWS Secrets Manager + environment-specific configs

---

## Development Rules System

### Rules Directory (`Rules/`)

**Purpose:** Centralized, organized rules for the workspace, divided by function.

**Total Rules:** 24 rule files covering all aspects of development and operations.

#### Rule Categories

1. **Core Development Rules (01-03)**
   - Development practices, code quality, testing
   - **Rule 01:** Automatic naming standards enforcement
   - **Rule 02:** Code quality standards
   - **Rule 03:** Testing requirements

2. **Infrastructure Rules (04-06)**
   - Deployment, environment, configuration
   - **Rule 04:** 11 deployment safety gates (includes 100% health confirmation)
   - **Rule 05:** Environment management
   - **Rule 06:** Configuration management

3. **Security & Organization (07-09)**
   - Security, documentation, workspace
   - **Rule 07:** Security practices
   - **Rule 08:** Documentation standards
   - **Rule 09:** Workspace organization

4. **Project-Specific Rules (10-12)**
   - Workspace structure, frontend, backend
   - **Rule 10:** Entity separation (NO shared code)
   - **Rule 11:** Alpine Analytics LLC Frontend rules
   - **Rule 12A:** Argo Capital Backend rules
   - **Rule 12B:** Alpine Analytics LLC Backend rules

5. **Trading & Operations (13-16)**
   - Trading operations, monitoring, backtesting, dev/prod differences
   - **Rule 13:** Trading operations
   - **Rule 14:** Monitoring & observability
   - **Rule 15:** Backtesting framework
   - **Rule 16:** Dev vs Prod differences

6. **Documentation & Optimization (17-19)**
   - SystemDocs management, versioning, continuous optimization
   - **Rule 17:** SystemDocs management
   - **Rule 18:** Versioning & archiving
   - **Rule 19:** Continuous optimization

7. **Code Organization & Standards (20-22)**
   - Intelligent code organization, dependency tracking, IP protection
   - **Rule 20:** Intelligent code organization (automatic enforcement)
   - **Rule 21:** Dependency & impact analysis (mandatory)
   - **Rule 22:** Trade secret & IP protection (mandatory)

8. **Operational & Strategic (23-24)**
   - Conversation logging, vision & strategic goals
   - **Rule 23:** Conversation logging system (LOCAL DEVELOPMENT ONLY)
   - **Rule 24:** Vision, mission, strategic goals, and decision-making framework

**Index:** `Rules/README.md` provides complete navigation

**Reference:** `.cursorrules/` files point to Rules directory

---

## Key Standards & Requirements

### 1. Automatic Naming Standards (Rule 01)

**Enforcement:** Code that doesn't follow naming conventions will be rejected.

**Standards:**
- Functions: `verb_noun` pattern (e.g., `calculate_position_size()`)
- Classes: `Noun` or `NounVerb` pattern (e.g., `RiskManager`)
- Variables: Descriptive, no abbreviations (e.g., `signal_confidence`)
- Constants: `CATEGORY_SPECIFIC_NAME` (e.g., `MAX_POSITION_SIZE_PCT`)
- Files: `feature_purpose` pattern (e.g., `risk_manager.py`)

### 2. Intelligent Code Organization (Rule 20)

**Enforcement:** Code organization is automatically enforced.

**Structure:**
- Feature-based modules (e.g., `risk_management/`, `strategies/`)
- Clear module boundaries
- Absolute imports only
- Tests mirror code structure

### 3. Dependency & Impact Analysis (Rule 21)

**Enforcement:** Impact analysis is mandatory before making changes.

**Requirements:**
- Identify all direct dependencies
- Identify all indirect dependencies
- Document impact analysis
- Update all affected components
- Test all affected components

### 4. Trade Secret & IP Protection (Rule 22)

**Enforcement:** IP protection is mandatory.

**Requirements:**
- Mark all trade secret code
- Mark all patent-pending code
- Restrict access to proprietary code
- NO exposure in code comments
- NO cross-entity IP sharing

### 5. 100% Health Confirmation (Rule 04 - Gate 11)

**Enforcement:** 100% health confirmation is MANDATORY after every deployment.

**Requirements:**
- Level 3 comprehensive health check
- ALL checks must pass
- Health confirmation documented
- Deployment NOT complete until 100% health confirmed

---

## Versioning & Archiving System

### Archive Structure (`archive/`)

**Purpose:** Maintain clean workspace while preserving complete history.

#### Archive Organization

```
archive/
├── docs/
│   ├── InvestorDocs/v1.0/ (archived versions)
│   ├── InvestorDocs/v2.0/ (archived versions)
│   ├── SystemDocs/v1.0/ (archived versions)
│   ├── SystemDocs/v2.0/ (archived versions)
│   └── TechnicalDocs/v1.0/ (archived versions)
├── configs/ (archived configuration versions)
├── scripts/ (archived script versions)
├── backup-files/ (legacy backup files)
└── INDEX.md (archive index)
```

#### Versioning Rules

- **Current versions:** Base name only (no version suffix)
- **Archived versions:** Include version number (e.g., `v2.0_*.md`)
- **Automatic archiving:** Old versions moved to archive when new versions created
- **Workspace cleanliness:** Only current versions visible in main directories

#### Automatic Cleanup

**When Requested:**
- Remove old backup directories
- Remove historical status files
- Remove log files (regenerate automatically)
- Remove old integration/work files
- Remove temporary files

**Safety:** Never removes source code, configs, or current documentation

**Reference:** `Rules/18_VERSIONING_ARCHIVING.md`

---

## Workspace Organization

### Directory Structure

```
workspace/
├── argo/                    # Argo Capital (INDEPENDENT ENTITY)
│   └── [Argo code - NO Alpine references]
├── alpine-backend/          # Alpine Analytics LLC (INDEPENDENT ENTITY)
│   └── [Alpine code - NO Argo references]
├── alpine-frontend/         # Alpine Analytics LLC (INDEPENDENT ENTITY)
│   └── [Alpine code - NO Argo references]
├── docs/                    # All documentation
│   ├── InvestorDocs/       # Investor documentation (v2.0 current)
│   ├── TechnicalDocs/      # Technical documentation
│   └── SystemDocs/         # System documentation (v4.0 current)
├── scripts/                 # Utility scripts
├── Rules/                   # Development rules (24 files)
├── archive/                 # Archived versions
├── backups/                 # Backup documentation only
└── [root config files]      # package.json, turbo.json, etc.
```

**Note:** NO `packages/shared/` directory - entities are completely separate.

### Clean Workspace Principles

- **Current versions only** in main directories
- **Old versions** automatically archived
- **Unnecessary files** removed on request
- **Complete history** preserved in archive
- **Entity separation** maintained

**Reference:** `Rules/09_WORKSPACE.md`, `Rules/18_VERSIONING_ARCHIVING.md`

---

## Backtesting Framework

### Strategy Backtester
- Tests signal generation quality
- Uses actual consensus engine
- Focus: Win rate, confidence accuracy
- For: Signal quality optimization

### Profit Backtester
- Tests trading profitability
- Includes slippage, fees
- Full execution simulation
- Focus: Returns, Sharpe ratio, drawdown
- For: Trading optimization

### Walk-Forward Testing
- Rolling window validation
- Train/test split
- Out-of-sample testing
- Parameter stability

---

## Deployment Architecture

### Local Development
- All code in workspace
- Local databases
- Dev Alpaca account (Argo)
- Local testing tools

### Production Deployment
- Code deployed via rsync
- Local-only files excluded
- Production Alpaca account (Argo)
- AWS Secrets Manager
- Production databases

### Deployment Exclusions
- Local setup scripts
- Test trade scripts
- Local documentation
- Test files
- Development configs

### Deployment Safety Gates (11 Gates)

1. Identify Changes
2. Verify Scope
3. Run Tests
4. Run Linting
5. Build Locally
6. Verify Staging
7. Validate Environment
8. Code Quality
9. Pre-Deployment Health
10. Explicit Confirmation
11. **100% Health Confirmation (MANDATORY)**

---

## Monitoring & Health Checks

### Health Check Levels

**Level 1: Basic**
- Environment detection
- Configuration validation

**Level 2: Standard**
- Trading engine connectivity (Argo)
- Signal service status
- Data sources availability
- Database connectivity

**Level 3: Comprehensive (MANDATORY for Production)**
- API endpoint testing
- AWS Secrets Manager access
- Full system integration
- **100% pass rate required**

### Health Check Scripts

- `argo/scripts/health_check_unified.py` - Unified (local + production)
- `scripts/full-health-check.sh` - Production health check

### 100% Health Confirmation Process

**After Every Deployment:**
1. Run Level 3 comprehensive health check
2. Verify ALL checks pass
3. Document health confirmation
4. Only mark deployment complete when 100% healthy

**Reference:** `Rules/04_DEPLOYMENT.md` - Gate 11

---

## Security Architecture

### Secret Management

**Local Development:**
- `config.json` (acceptable for local)
- Environment variables

**Production:**
- AWS Secrets Manager (primary)
- Environment-specific secrets
- Encrypted at rest

### Security Features

- CORS whitelist (no wildcards)
- Security headers middleware
- Input validation & sanitization
- SQL injection protection
- Rate limiting
- Authentication/authorization
- Error message sanitization

### Trade Secret & IP Protection

- Trade secret code marking
- Patent-pending code marking
- Access controls
- Encrypted storage
- Audit logging
- Entity separation (protects IP)

**Reference:** `Rules/22_TRADE_SECRET_IP_PROTECTION.md`

### Strategic Direction & Goals

**Vision:** "To democratize access to institutional-grade trading signals through transparent, adaptive AI technology."

**Mission:**
- **Alpine Analytics LLC:** Provide the highest-quality, most transparent trading signals to customers
- **Argo Capital:** Optimize trading profitability through proprietary algorithms and rigorous risk management

**Strategic Goals:**
1. Maintain 96%+ win rate (current: 96.2%)
2. Scale customer base and revenue (Year 1: $2.4M ARR target)
3. Achieve 100% signal verification and auditability
4. Maintain 99.9% system uptime
5. Build world-class technology infrastructure
6. Protect intellectual property and trade secrets
7. Build scalable operations
8. Achieve strategic market position

**Decision-Making Framework:**
- All decisions align with vision and mission
- All work prioritizes strategic goals
- Clear KPIs track progress
- Measurable success metrics

**Reference:** `Rules/24_VISION_MISSION_GOALS.md`

### Conversation Logging System

**Purpose:** Automatic logging of user-AI conversations for reference and context.

**Features:**
- Local development only (never deployed)
- Cursor-aware (pauses when Cursor not running)
- 3-day retention for full conversations
- 30-day retention for decision summaries
- Automatic cleanup
- Privacy-focused (local-only, no cloud)

**Reference:** `Rules/23_CONVERSATION_LOGGING.md`

---

## Performance Tracking

### Trade Journaling
- Every trade logged
- Entry/exit details
- P&L tracking
- Performance metrics

### Performance Metrics
- Win rate
- Total return
- Sharpe ratio
- Max drawdown
- Profit factor

---

## API Endpoints

### Argo Capital API (`http://localhost:8000` or production)

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /api/signals/latest` - Latest signals
- `GET /api/signals/stats` - Signal statistics
- `GET /api/performance/win-rate` - Performance metrics

### Alpine Analytics LLC API (`http://localhost:9001` or production)

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/signals/subscribed` - User's signals
- `GET /api/signals/history` - Signal history
- `POST /api/v1/external-signals/sync/signal` - External signal provider integration

---

## Configuration Management

### Argo Capital config.json Structure

```json
{
  "massive": { "api_key": "...", "enabled": true },
  "alpha_vantage": { "api_key": "...", "enabled": true },
  "x_api": { "bearer_token": "...", "enabled": true },
  "sonar": { "api_key": "...", "enabled": true },
  "alpaca": {
    "dev": { "api_key": "...", "secret_key": "..." },
    "production": { "api_key": "...", "secret_key": "..." }
  },
  "strategy": {
    "weight_massive": 0.4,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.2,
    "weight_sonar": 0.15
  },
  "trading": {
    "min_confidence": 75.0,
    "auto_execute": true,
    "position_size_pct": 10,
    "max_drawdown_pct": 10
  },
  "backtest": { ... }
}
```

### Alpine Analytics LLC Configuration

- Environment variables (`.env`)
- AWS Secrets Manager (production)
- Database configuration
- External signal provider API key

---

## Operational Procedures

### Starting the System

**Local:**
```bash
# Argo Capital
cd argo
python main.py

# Alpine Analytics LLC
cd alpine-backend
python -m backend.main
cd ../alpine-frontend
npm run dev
```

**Production:**
```bash
# Deploy Argo Capital (Blue-Green Zero-Downtime)
./scripts/deploy-argo-blue-green.sh

# Deploy Alpine Analytics LLC (Blue-Green Zero-Downtime)
./scripts/deploy-alpine.sh
```

### Monitoring

- Check health: `python argo/scripts/health_check_unified.py --level 3`
- View logs: `tail -f /tmp/argo.log`
- Check positions: Alpaca dashboard
- Monitor performance: Performance tracker

### Post-Deployment Verification

**MANDATORY:**
1. Run Level 3 comprehensive health check
2. Verify 100% pass rate
3. Document health confirmation
4. Only mark deployment complete when 100% healthy

---

## Data Flow Diagrams

### Argo Capital: Signal Generation → Trading

```
Data Sources → Consensus Engine → Signal Generation
    ↓
Risk Validation → Position Sizing → Order Execution
    ↓
Position Management → Performance Tracking
```

### Deployment Architecture

**Argo Blue-Green Deployment:**
- Blue Environment: `/root/argo-production-blue` (port 8000 when active)
- Green Environment: `/root/argo-production-green` (port 8001 when staging)
- Zero-downtime deployments with automatic rollback
- Health checks (Gate 11) before traffic switch

**Alpine Blue-Green Deployment:**
- Blue Environment: Docker Compose on ports 8001/3000
- Green Environment: Docker Compose on ports 8002/3002
- Zero-downtime deployments with nginx traffic switching

### Alpine Analytics LLC: Signal Distribution

```
External Signal Provider (API) → Alpine Backend API
    ↓
PostgreSQL Storage → WebSocket Push
    ↓
Frontend Dashboard → User Notification
```

---

## File Organization

### Local-Only Files (Never Deployed)

- `scripts/local_*.sh` - Local setup/validation
- `argo/scripts/execute_test_trade.py` - Test trade
- `argo/scripts/enable_full_trading.py` - Enable trading
- `docs/LOCAL_*.md` - Local documentation

### Production Files (Always Deployed)

- `argo/argo/**/*.py` - Core application code
- `argo/main.py` - API server
- `argo/requirements.txt` - Dependencies
- `argo/scripts/check_account_status.py` - Operational tools
- `argo/scripts/monitor_aws_secrets_health.py` - Monitoring

### Environment-Aware Files (Deploy, Adapt Behavior)

- `argo/argo/core/paper_trading_engine.py` - Detects environment
- `argo/argo/core/signal_generation_service.py` - Environment-aware
- `argo/scripts/health_check_unified.py` - Works in both

---

## Next Steps

1. Review this architecture document
2. Run local setup: `./scripts/local_setup.sh`
3. Run health checks: `python argo/scripts/health_check_unified.py --level 2`
4. Execute test trade: `python argo/scripts/execute_test_trade.py`
5. Enable full trading: `python argo/scripts/enable_full_trading.py`
6. Deploy to production: `./scripts/deploy-argo.sh` or `./scripts/deploy-alpine.sh`
7. **Verify 100% health confirmation** (Gate 11)

---

**Last Updated:** January 15, 2025  
**Version:** 4.0

**Key Changes from v3.0:**
- Added Rule 23: Conversation logging system (local development only)
- Added Rule 24: Vision, mission, strategic goals, and decision-making framework
- Updated rule count (24 rules)
- Strategic alignment framework documented
- Vision and mission statements integrated
- Strategic goals and metrics documented
- Decision-making framework added

**Key Changes from v2.0:**
- Complete entity separation documented
- New rules (20, 21, 22, 23, 24) documented
- 100% health confirmation requirement added
- Automatic naming and organization standards documented
- Trade secret/IP protection documented
- Dependency tracking requirements documented
- Removed all cross-entity references
