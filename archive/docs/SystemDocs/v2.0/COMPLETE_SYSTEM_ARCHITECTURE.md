# Complete System Architecture Documentation

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Complete System Overview

---

## Executive Summary

This document provides a comprehensive, front-to-end overview of the Argo-Alpine trading signal platform architecture, covering all components, data flows, and operational procedures.

---

## System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARGO-ALPINE PLATFORM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   ARGO CAPITAL   │         │ ALPINE ANALYTICS │            │
│  │  (Signal Gen)    │────────▶│  (Distribution)  │            │
│  └──────────────────┘         └──────────────────┘            │
│         │                              │                        │
│         │                              │                        │
│         ▼                              ▼                        │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │  Paper Trading   │         │   PostgreSQL     │            │
│  │  (Alpaca API)    │         │   (Signals DB)   │            │
│  └──────────────────┘         └──────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Argo Capital (Signal Generation)

**Location:** `argo/`

#### Core Components

1. **Signal Generation Service** (`argo/core/signal_generation_service.py`)
   - Generates signals every 5 seconds
   - Uses Weighted Consensus v6.0
   - Integrates 4 data sources
   - Applies risk management
   - Executes trades (if enabled)

2. **Weighted Consensus Engine** (`argo/core/weighted_consensus_engine.py`)
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
Market Data → Data Sources → Weighted Consensus → Signal Generation
    ↓
Risk Validation → Trade Execution → Position Management
    ↓
Performance Tracking → Alpine Sync
```

---

### 2. Alpine Analytics (Signal Distribution)

**Location:** `alpine-backend/` + `alpine-frontend/`

#### Core Components

1. **Backend API** (`alpine-backend/backend/main.py`)
   - User authentication
   - Signal distribution
   - Subscription management
   - WebSocket real-time updates

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

---

## Environment Setup

### Development Environment

- **Location:** Local machine
- **Alpaca Account:** Dev paper trading account
- **Database:** SQLite (local)
- **Config:** `argo/config.json` (local)

### Production Environment

- **Argo Server:** 178.156.194.174
- **Alpine Server:** 91.98.153.49
- **Alpaca Account:** Production paper trading account
- **Database:** PostgreSQL (production)
- **Config:** AWS Secrets Manager + `/root/argo-production/config.json`

---

## Signal Generation Flow

### Step-by-Step Process

1. **Data Collection** (Every 5 seconds)
   - Fetch data from all 4 sources
   - Parse and normalize data

2. **Consensus Calculation**
   - Each source votes (LONG/SHORT)
   - Weighted voting algorithm
   - Calculate consensus confidence

3. **Signal Validation**
   - Check 75% confidence threshold
   - Apply risk management rules
   - Check correlation limits
   - Validate account status

4. **Trade Execution** (if auto_execute enabled)
   - Calculate position size
   - Submit order to Alpaca
   - Place stop-loss/take-profit
   - Track order status

5. **Signal Storage**
   - Store in SQLite (Argo)
   - Sync to PostgreSQL (Alpine)
   - Generate SHA-256 hash
   - Create audit trail

6. **Distribution**
   - Push to Alpine backend
   - WebSocket notification
   - Email alerts (if configured)

---

## Trading Execution Flow

### Order Lifecycle

1. **Signal Generated** → Validated → Risk checks passed
2. **Position Size Calculated** → Based on confidence, volatility, account size
3. **Order Submitted** → Market or limit order
4. **Order Filled** → Position created
5. **Stop-Loss/Take-Profit Placed** → Bracket orders
6. **Position Monitored** → Auto-exit on targets
7. **Trade Closed** → P&L recorded → Performance tracked

---

## Risk Management

### Risk Checks (Applied Before Every Trade)

1. **Account Status**
   - Trading not blocked
   - Account not blocked
   - Sufficient buying power

2. **Daily Loss Limit**
   - Check daily P&L
   - Pause trading if limit exceeded

3. **Drawdown Limit**
   - Track peak equity
   - Calculate current drawdown
   - Block trades if max drawdown exceeded

4. **Position Limits**
   - Check existing positions
   - Enforce correlation limits
   - Prevent over-concentration

5. **Position Sizing**
   - Base size: 10% of capital
   - Adjusted by confidence
   - Adjusted by volatility
   - Max size: 15% of capital

---

## Data Sources Integration

### Massive.com (40% weight)
- Primary market data
- Price action analysis
- Trend detection

### Alpha Vantage (25% weight)
- Technical indicators
- RSI, MACD, Moving averages
- Technical analysis

### X Sentiment (20% weight)
- Social media sentiment
- News sentiment
- Market sentiment analysis

### Sonar AI (15% weight)
- AI-powered analysis
- Pattern recognition
- Advanced analytics

---

## Development Rules System

### Rules Directory (`Rules/`)

**Purpose:** Centralized, organized rules for the Argo-Alpine system, divided by function.

**Total Rules:** 18 rule files covering all aspects of development and operations.

#### Rule Categories

1. **Core Development Rules (01-03)**
   - Development practices, code quality, testing

2. **Infrastructure Rules (04-06)**
   - Deployment, environment, configuration

3. **Security & Organization (07-09)**
   - Security, documentation, workspace

4. **Project-Specific Rules (10-12)**
   - Monorepo, frontend, backend

5. **Trading & Operations (13-16)**
   - Trading operations, monitoring, backtesting, dev/prod differences

6. **Documentation & Versioning (17-18)**
   - SystemDocs management, versioning & archiving

**Index:** `Rules/README.md` provides complete navigation

**Reference:** `.cursorrules/` files point to Rules directory

---

## Versioning & Archiving System

### Archive Structure (`archive/`)

**Purpose:** Maintain clean workspace while preserving complete history.

#### Archive Organization

```
archive/
├── docs/
│   ├── InvestorDocs/v1.0/ (archived versions)
│   ├── SystemDocs/v1.0/ (archived versions)
│   └── TechnicalDocs/v1.0/ (archived versions)
├── configs/ (archived configuration versions)
├── scripts/ (archived script versions)
├── backup-files/ (legacy backup files)
└── INDEX.md (archive index)
```

#### Versioning Rules

- **Current versions:** Base name only (no version suffix)
- **Archived versions:** Include version number (e.g., `v1.0_01_*.md`)
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
argo-alpine-workspace/
├── argo/                    # Argo Capital (Trading Engine)
├── alpine-backend/          # Alpine Analytics Backend
├── alpine-frontend/         # Alpine Analytics Frontend
├── packages/shared/         # Shared utilities
├── docs/                    # All documentation
│   ├── InvestorDocs/       # Investor documentation (v2.0 current)
│   ├── TechnicalDocs/      # Technical documentation
│   └── SystemDocs/         # System documentation (53 files)
├── scripts/                 # Utility scripts (51 files)
├── Rules/                   # Development rules (18 files)
├── archive/                 # Archived versions
├── backups/                 # Backup documentation only
├── logs/                    # Log files (regenerated)
└── [root config files]      # package.json, turbo.json, etc.
```

### Clean Workspace Principles

- **Current versions only** in main directories
- **Old versions** automatically archived
- **Unnecessary files** removed on request
- **Complete history** preserved in archive

**Reference:** `Rules/09_WORKSPACE.md`, `Rules/18_VERSIONING_ARCHIVING.md`

---

## Backtesting Framework

### Strategy Backtester
- Tests signal generation quality
- Uses actual WeightedConsensusEngine
- Focus: Win rate, confidence accuracy
- For: Alpine customer signal quality

### Profit Backtester
- Tests trading profitability
- Includes slippage, fees
- Full execution simulation
- Focus: Returns, Sharpe ratio, drawdown
- For: Argo trading optimization

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
- Dev Alpaca account
- Local testing tools

### Production Deployment
- Code deployed via rsync
- Local-only files excluded
- Production Alpaca account
- AWS Secrets Manager
- Production databases

### Deployment Exclusions
- Local setup scripts
- Test trade scripts
- Local documentation
- Test files
- Development configs

---

## Monitoring & Health Checks

### Health Check Levels

**Level 1: Basic**
- Environment detection
- Configuration validation

**Level 2: Standard**
- Trading engine connectivity
- Signal service status
- Data sources availability
- Database connectivity

**Level 3: Comprehensive**
- API endpoint testing
- AWS Secrets Manager access
- Full system integration

### Health Check Scripts

- `scripts/local_health_check.sh` - Local validation
- `argo/scripts/health_check_unified.py` - Unified (local + production)
- `scripts/full-health-check.sh` - Production health check

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

### Argo API (`http://localhost:8000` or production)

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /api/signals/latest` - Latest signals
- `GET /api/signals/stats` - Signal statistics
- `GET /api/performance/win-rate` - Performance metrics

### Alpine API (`http://localhost:9001` or production)

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/signals/subscribed` - User's signals
- `GET /api/signals/history` - Signal history

---

## Configuration Management

### config.json Structure

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

---

## Operational Procedures

### Starting the System

**Local:**
```bash
./scripts/local_setup.sh
./scripts/local_health_check.sh
python argo/scripts/execute_test_trade.py  # Optional
python argo/scripts/enable_full_trading.py  # After test trade
```

**Production:**
```bash
./scripts/deploy-argo.sh
./scripts/deploy-alpine.sh
```

### Monitoring

- Check health: `python argo/scripts/health_check_unified.py --level 3`
- View logs: `tail -f /tmp/argo.log`
- Check positions: Alpaca dashboard
- Monitor performance: Performance tracker

### Troubleshooting

1. Check environment: `python -c "from argo.core.environment import detect_environment; print(detect_environment())"`
2. Verify Alpaca connection: `python argo/scripts/check_account_status.py`
3. Run health check: `./scripts/local_health_check.sh`
4. Check logs for errors

---

## Data Flow Diagrams

### Signal Generation → Trading

```
Data Sources → Consensus Engine → Signal Generation
    ↓
Risk Validation → Position Sizing → Order Execution
    ↓
Position Management → Performance Tracking
```

### Signal Distribution

```
Argo Signal Generation → SQLite Storage
    ↓
Alpine Sync API → PostgreSQL Storage
    ↓
WebSocket Push → Frontend Dashboard
    ↓
User Notification
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
3. Run health checks: `./scripts/local_health_check.sh`
4. Execute test trade: `python argo/scripts/execute_test_trade.py`
5. Enable full trading: `python argo/scripts/enable_full_trading.py`
6. Deploy to production: `./scripts/deploy-argo.sh`

---

**Last Updated:** January 15, 2025  
**Version:** 2.0

