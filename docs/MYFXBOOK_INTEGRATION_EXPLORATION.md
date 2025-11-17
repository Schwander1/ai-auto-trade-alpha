# MyFXBook Integration Exploration

## Executive Summary

This document explores the integration of **MyFXBook** into the Argo Capital / Alpine Analytics trading system. MyFXBook is a third-party performance tracking and verification platform primarily used for forex trading, but can also track stocks and other asset classes. This integration would provide external verification and transparency of trading performance.

**Date:** 2025-01-XX  
**Status:** Exploration Phase  
**Priority:** Medium

---

## 1. What is MyFXBook?

### Overview
MyFXBook is a web-based platform that:
- **Tracks trading performance** across multiple brokers and accounts
- **Verifies trading results** through broker account connections
- **Provides analytics** including equity curves, drawdowns, win rates, and risk metrics
- **Enables transparency** by allowing public sharing of verified trading results
- **Offers API access** for programmatic integration

### Key Features
- **Account Verification:** Connects directly to broker accounts (MT4, MT5, cTrader, etc.)
- **Performance Analytics:** Comprehensive metrics including Sharpe ratio, profit factor, max drawdown
- **Public/Private Sharing:** Share verified results publicly or keep private
- **Community Features:** Follow other traders, view community sentiment
- **API Access:** RESTful API for programmatic access to account data

### Use Cases for Argo/Alpine
1. **External Verification:** Provide third-party verification of trading performance
2. **Transparency:** Share verified results with investors/clients
3. **Marketing:** Use verified performance metrics for marketing materials
4. **Compliance:** Demonstrate track record for regulatory purposes
5. **Analytics:** Leverage MyFXBook's analytics alongside internal tracking

---

## 2. Current System Architecture

### 2.1 Performance Tracking System

**Location:** `argo/argo/tracking/unified_tracker.py`

The system currently has a comprehensive `UnifiedPerformanceTracker` that tracks:

```python
@dataclass
class Trade:
    id: str
    signal_id: str
    asset_class: str  # "stock" or "crypto"
    symbol: str
    signal_type: str  # "long" or "short"
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_timestamp: str
    exit_timestamp: Optional[str]
    holding_period_hours: Optional[float]
    pnl_dollars: Optional[float]
    pnl_percent: Optional[float]
    outcome: str  # "win", "loss", "pending"
    confidence: float
    verification_hash: str
    # ... additional fields for slippage, commissions, etc.
```

**Key Capabilities:**
- Tracks all trades with comprehensive metadata
- Calculates P&L, win rates, and performance metrics
- Stores in Redis or in-memory fallback
- Provides API endpoints for performance data
- Includes verification hashes for audit trail

### 2.2 Trading Execution

**Location:** `argo/argo/core/paper_trading_engine.py`

The `PaperTradingEngine` executes trades through:
- **Alpaca API** for stock trading (paper and live)
- **Position management** with stop loss and take profit orders
- **Risk management** with position sizing based on confidence and volatility

**Current Integrations:**
- Notion Pro (instant signal logging)
- Tradervue Gold (trade tracking)
- Power BI (streaming analytics)

### 2.3 Performance API

**Location:** `argo/argo/api/performance.py`

Provides REST endpoints:
- `GET /api/v1/performance/win-rate` - Win rate statistics
- `GET /api/v1/performance/roi` - ROI calculations
- `GET /api/v1/performance/equity-curve` - Equity curve data

---

## 3. MyFXBook API Overview

### 3.1 Authentication

MyFXBook uses **session-based authentication**:
- Login with email/password to get session token
- Sessions are **IP-bound** and expire after 1 month
- Sessions valid only from login IP
- Use logout method to revoke sessions early

### 3.2 Key API Endpoints

Based on MyFXBook API documentation:

1. **Authentication**
   - `POST /api/login.json` - Login and get session
   - `POST /api/logout.json` - Logout and revoke session

2. **Account Data**
   - `GET /api/get-my-accounts.json` - Get user's accounts
   - `GET /api/get-account.json` - Get account details
   - `GET /api/get-open-trades.json` - Get open trades
   - `GET /api/get-open-orders.json` - Get open orders
   - `GET /api/get-history.json` - Get trading history

3. **Performance Metrics**
   - `GET /api/get-daily-gain.json` - Daily gain values
   - `GET /api/get-gain.json` - Gain between dates
   - `GET /api/get-community-outlook.json` - Community sentiment

4. **Widgets**
   - `GET /api/get-widget.json` - Generate custom widgets

### 3.3 Data Format

**Trade Data Structure:**
```json
{
  "id": 12345,
  "openTime": "2024-01-15 10:30:00",
  "closeTime": "2024-01-15 14:45:00",
  "symbol": "EURUSD",
  "type": "buy",  // or "sell"
  "volume": 0.1,
  "openPrice": 1.0850,
  "closePrice": 1.0875,
  "profit": 25.00,
  "swap": 0.00,
  "commission": 0.00
}
```

**Account Data Structure:**
```json
{
  "id": 12345,
  "name": "Alpaca Paper Account",
  "server": "Alpaca",
  "platform": "API",
  "currency": "USD",
  "balance": 10000.00,
  "equity": 10250.00,
  "profit": 250.00,
  "margin": 500.00,
  "freeMargin": 9750.00
}
```

### 3.4 Limitations & Considerations

1. **Forex-Focused:** Primarily designed for forex (MT4/MT5), but supports other brokers
2. **Broker Connection Required:** Need to connect broker account (Alpaca may not be directly supported)
3. **Session Management:** IP-bound sessions require careful handling
4. **Rate Limits:** API has rate limits (not publicly documented)
5. **Data Timestamps:** Transaction timestamps in broker's local timezone

---

## 4. Integration Architecture

### 4.1 Integration Approach

**Option A: Direct API Integration (Recommended)**
- Create MyFXBook client module
- Sync trades from `UnifiedPerformanceTracker` to MyFXBook
- Pull performance metrics from MyFXBook API
- Display MyFXBook widgets/links in Alpine frontend

**Option B: Broker Account Connection**
- Connect Alpaca account directly to MyFXBook (if supported)
- Automatic trade synchronization
- Real-time performance tracking

**Option C: Hybrid Approach**
- Use MyFXBook API for manual trade submission
- Use broker connection for automatic verification
- Combine both data sources for comprehensive tracking

### 4.2 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Argo Trading System                       │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ UnifiedTracker   │────────▶│ PaperTradingEngine│         │
│  │ (Trade Storage)  │         │ (Execution)       │         │
│  └──────────────────┘         └──────────────────┘         │
│         │                              │                    │
│         │                              │                    │
│         ▼                              ▼                    │
│  ┌──────────────────────────────────────────────┐          │
│  │      MyFXBook Integration Module              │          │
│  │  ┌────────────────────────────────────────┐  │          │
│  │  │  MyFXBookClient                        │  │          │
│  │  │  - Authentication                      │  │          │
│  │  │  - Trade Sync                          │  │          │
│  │  │  - Performance Fetch                   │  │          │
│  │  └────────────────────────────────────────┘  │          │
│  │  ┌────────────────────────────────────────┐  │          │
│  │  │  TradeMapper                           │  │          │
│  │  │  - Argo Trade → MyFXBook Format        │  │          │
│  │  │  - Handle asset class differences      │  │          │
│  │  └────────────────────────────────────────┘  │          │
│  └──────────────────────────────────────────────┘          │
│         │                                                   │
│         │ HTTPS API                                         │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────┐          │
│  │         MyFXBook Platform                     │          │
│  │  - Account Verification                       │          │
│  │  - Performance Analytics                      │          │
│  │  - Public/Private Sharing                     │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │
         │ API / Widget Embed
         ▼
┌──────────────────────────────────────────────┐
│      Alpine Analytics Frontend                │
│  - Display MyFXBook verified metrics          │
│  - Embed MyFXBook widgets                     │
│  - Link to public MyFXBook profile            │
└──────────────────────────────────────────────┘
```

### 4.3 Data Flow

1. **Trade Execution:**
   - Trade executed via `PaperTradingEngine`
   - Trade recorded in `UnifiedPerformanceTracker`
   - Trade synced to MyFXBook via integration module

2. **Performance Tracking:**
   - Internal metrics calculated by `UnifiedPerformanceTracker`
   - External metrics fetched from MyFXBook API
   - Both displayed in Alpine frontend

3. **Verification:**
   - MyFXBook provides third-party verification
   - Verification status displayed alongside internal metrics
   - Public MyFXBook profile linked for transparency

---

## 5. Implementation Plan

### 5.1 Phase 1: Core Integration Module

**Create:** `argo/argo/integrations/myfxbook_client.py`

**Features:**
- Authentication (login/logout)
- Session management (IP-bound handling)
- Trade submission
- Performance data fetching
- Error handling and retry logic

**Dependencies:**
- `requests` (already in requirements.txt)
- Session management for IP-bound sessions

### 5.2 Phase 2: Trade Synchronization

**Create:** `argo/argo/integrations/myfxbook_sync.py`

**Features:**
- Map Argo trades to MyFXBook format
- Handle asset class differences (stocks vs forex)
- Batch trade submission
- Conflict resolution (duplicate detection)
- Sync status tracking

**Challenges:**
- **Asset Class Mapping:** MyFXBook is forex-focused, need to map stocks/crypto
- **Symbol Format:** Convert "AAPL" to MyFXBook format (may need custom mapping)
- **Time Zones:** Handle timezone differences
- **Partial Fills:** Handle partial fills appropriately

### 5.3 Phase 3: Performance Integration

**Enhance:** `argo/argo/api/performance.py`

**Features:**
- Fetch MyFXBook metrics alongside internal metrics
- Compare internal vs MyFXBook metrics
- Display verification status
- Embed MyFXBook widgets

### 5.4 Phase 4: Frontend Integration

**Enhance:** `alpine-frontend/`

**Features:**
- Display MyFXBook verified metrics
- Embed MyFXBook widgets (balance chart, growth chart)
- Link to public MyFXBook profile
- Show verification badge

---

## 6. Code Structure

### 6.1 MyFXBook Client

```python
# argo/argo/integrations/myfxbook_client.py

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MyFXBookClient:
    """MyFXBook API Client"""
    
    BASE_URL = "https://www.myfxbook.com/api"
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session_token: Optional[str] = None
        self.logged_in = False
    
    def login(self) -> bool:
        """Login and get session token"""
        try:
            response = self.session.post(
                f"{self.BASE_URL}/login.json",
                json={
                    "email": self.email,
                    "password": self.password
                },
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                logger.error(f"MyFXBook login error: {data.get('message')}")
                return False
            
            self.session_token = data.get("session")
            self.logged_in = True
            logger.info("✅ MyFXBook login successful")
            return True
        except Exception as e:
            logger.error(f"MyFXBook login failed: {e}")
            return False
    
    def logout(self) -> bool:
        """Logout and revoke session"""
        if not self.logged_in:
            return True
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/logout.json",
                json={"session": self.session_token},
                timeout=10
            )
            self.logged_in = False
            self.session_token = None
            return True
        except Exception as e:
            logger.error(f"MyFXBook logout failed: {e}")
            return False
    
    def get_accounts(self) -> List[Dict]:
        """Get user's accounts"""
        if not self.logged_in:
            if not self.login():
                return []
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/get-my-accounts.json",
                params={"session": self.session_token},
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                logger.error(f"MyFXBook error: {data.get('message')}")
                return []
            
            return data.get("accounts", [])
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return []
    
    def submit_trade(self, trade_data: Dict) -> bool:
        """Submit trade to MyFXBook"""
        # Note: MyFXBook API may not support direct trade submission
        # May need to use broker connection instead
        # This is a placeholder for the API structure
        pass
    
    def get_performance_metrics(self, account_id: int) -> Dict:
        """Get performance metrics for account"""
        if not self.logged_in:
            if not self.login():
                return {}
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/get-account.json",
                params={
                    "session": self.session_token,
                    "id": account_id
                },
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                logger.error(f"MyFXBook error: {data.get('message')}")
                return {}
            
            return data.get("account", {})
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
```

### 6.2 Trade Mapper

```python
# argo/argo/integrations/myfxbook_mapper.py

from typing import Dict, Optional
from datetime import datetime
from argo.tracking.unified_tracker import Trade

class MyFXBookTradeMapper:
    """Map Argo trades to MyFXBook format"""
    
    # Symbol mapping for stocks to MyFXBook format
    SYMBOL_MAP = {
        "AAPL": "AAPL.US",
        "NVDA": "NVDA.US",
        # Add more mappings as needed
    }
    
    @staticmethod
    def map_trade(trade: Trade) -> Optional[Dict]:
        """Convert Argo Trade to MyFXBook format"""
        
        # MyFXBook primarily supports forex, stocks may need special handling
        if trade.asset_class == "crypto":
            # Crypto may not be directly supported
            logger.warning(f"Crypto trades may not be supported: {trade.symbol}")
            return None
        
        # Map symbol
        symbol = MyFXBookTradeMapper.SYMBOL_MAP.get(
            trade.symbol, 
            trade.symbol
        )
        
        # Map signal type to MyFXBook type
        trade_type = "buy" if trade.signal_type == "long" else "sell"
        
        # Calculate profit (MyFXBook expects profit in account currency)
        profit = trade.pnl_dollars if trade.pnl_dollars else 0.0
        
        # Format timestamps
        open_time = datetime.fromisoformat(trade.entry_timestamp)
        close_time = (
            datetime.fromisoformat(trade.exit_timestamp) 
            if trade.exit_timestamp 
            else datetime.utcnow()
        )
        
        return {
            "symbol": symbol,
            "type": trade_type,
            "volume": trade.quantity,
            "openPrice": trade.entry_price,
            "closePrice": trade.exit_price or trade.entry_price,
            "openTime": open_time.strftime("%Y-%m-%d %H:%M:%S"),
            "closeTime": close_time.strftime("%Y-%m-%d %H:%M:%S"),
            "profit": profit,
            "swap": 0.0,  # Not applicable for stocks
            "commission": trade.commission or 0.0
        }
```

### 6.3 Integration Service

```python
# argo/argo/integrations/myfxbook_integration.py

from typing import List, Optional
from argo.tracking.unified_tracker import UnifiedPerformanceTracker, Trade
from argo.integrations.myfxbook_client import MyFXBookClient
from argo.integrations.myfxbook_mapper import MyFXBookTradeMapper
import logging

logger = logging.getLogger(__name__)

class MyFXBookIntegration:
    """Integration service for MyFXBook"""
    
    def __init__(
        self, 
        email: str, 
        password: str,
        tracker: Optional[UnifiedPerformanceTracker] = None
    ):
        self.client = MyFXBookClient(email, password)
        self.tracker = tracker or UnifiedPerformanceTracker()
        self.mapper = MyFXBookTradeMapper()
        self.synced_trade_ids = set()  # Track synced trades
    
    def sync_trade(self, trade: Trade) -> bool:
        """Sync single trade to MyFXBook"""
        try:
            # Map trade to MyFXBook format
            myfxbook_trade = self.mapper.map_trade(trade)
            if not myfxbook_trade:
                return False
            
            # Submit to MyFXBook
            # Note: Actual implementation depends on MyFXBook API capabilities
            success = self.client.submit_trade(myfxbook_trade)
            
            if success:
                self.synced_trade_ids.add(trade.id)
                logger.info(f"✅ Synced trade {trade.id} to MyFXBook")
            
            return success
        except Exception as e:
            logger.error(f"Failed to sync trade {trade.id}: {e}")
            return False
    
    def sync_recent_trades(self, days: int = 30) -> int:
        """Sync recent trades to MyFXBook"""
        trades = self.tracker._get_recent_trades(days=days)
        synced_count = 0
        
        for trade in trades:
            # Skip if already synced
            if trade.id in self.synced_trade_ids:
                continue
            
            # Only sync completed trades
            if trade.outcome == "pending":
                continue
            
            if self.sync_trade(trade):
                synced_count += 1
        
        logger.info(f"✅ Synced {synced_count} trades to MyFXBook")
        return synced_count
    
    def get_verified_metrics(self, account_id: int) -> Dict:
        """Get verified performance metrics from MyFXBook"""
        return self.client.get_performance_metrics(account_id)
```

---

## 7. Configuration

### 7.1 Environment Variables

Add to `.env` or `config.json`:

```json
{
  "myfxbook": {
    "enabled": true,
    "email": "your-email@example.com",
    "password": "your-password",
    "account_id": 12345,
    "sync_interval_minutes": 60,
    "auto_sync": true
  }
}
```

### 7.2 Secrets Management

Use AWS Secrets Manager (already integrated):

```python
from argo.utils.secrets_manager import get_secret

myfxbook_email = get_secret("myfxbook-email", service="argo")
myfxbook_password = get_secret("myfxbook-password", service="argo")
```

---

## 8. Challenges & Considerations

### 8.1 Technical Challenges

1. **Broker Support:**
   - MyFXBook primarily supports MT4/MT5 brokers
   - Alpaca may not be directly supported
   - May need to use manual trade submission or find alternative

2. **Asset Class Differences:**
   - MyFXBook is forex-focused
   - Stocks/crypto may need custom handling
   - Symbol format differences

3. **Session Management:**
   - IP-bound sessions require careful handling
   - May need proxy or VPN for consistent IP
   - Session expiration handling

4. **Data Synchronization:**
   - Handling duplicate trades
   - Conflict resolution
   - Partial sync failures

### 8.2 Business Considerations

1. **Cost:**
   - MyFXBook may have subscription fees
   - API access may require premium account

2. **Privacy:**
   - Public sharing vs private tracking
   - Data ownership and control

3. **Reliability:**
   - Dependency on third-party service
   - API availability and rate limits

### 8.3 Alternatives

If MyFXBook integration proves challenging, consider:

1. **Tradervue** (already integrated)
   - Better stock/crypto support
   - Already in use

2. **Custom Verification System**
   - Build internal verification
   - Use blockchain for immutable records

3. **Other Platforms:**
   - TradingView (performance tracking)
   - ZuluTrade (social trading)
   - eToro (copy trading)

---

## 9. Next Steps

### Immediate Actions

1. **Research MyFXBook API:**
   - Review official API documentation
   - Test API endpoints
   - Verify Alpaca broker support

2. **Create Proof of Concept:**
   - Implement basic client
   - Test authentication
   - Test trade submission (if supported)

3. **Evaluate Alternatives:**
   - Compare with Tradervue (already integrated)
   - Assess cost/benefit
   - Consider other platforms

### Decision Points

1. **Broker Support:**
   - Can Alpaca be connected to MyFXBook?
   - If not, is manual submission viable?

2. **Asset Class Support:**
   - Can stocks/crypto be tracked?
   - What are the limitations?

3. **Integration Priority:**
   - Is MyFXBook worth the effort vs alternatives?
   - What's the ROI?

---

## 10. References

- [MyFXBook API Documentation](https://www.myfxbook.com/api)
- [MyFXBook Platform](https://www.myfxbook.com)
- Current System: `argo/argo/tracking/unified_tracker.py`
- Current Integrations: `argo/argo/integrations/complete_tracking.py`

---

## Appendix A: MyFXBook API Endpoints (Reference)

### Authentication
- `POST /api/login.json` - Login
- `POST /api/logout.json` - Logout

### Account Management
- `GET /api/get-my-accounts.json` - List accounts
- `GET /api/get-account.json` - Get account details
- `GET /api/get-open-trades.json` - Get open trades
- `GET /api/get-open-orders.json` - Get open orders
- `GET /api/get-history.json` - Get trading history

### Performance
- `GET /api/get-daily-gain.json` - Daily gain
- `GET /api/get-gain.json` - Gain between dates
- `GET /api/get-community-outlook.json` - Community sentiment

### Widgets
- `GET /api/get-widget.json` - Generate widget

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Author:** System Exploration  
**Status:** Draft - Pending API Verification

