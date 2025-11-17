# Additional Refactoring Analysis: Functions Over 50 Lines

## Summary

Found **2 additional functions** over 50 lines in other parts of the codebase that should be refactored for better maintainability, testability, and readability.

---

## 1. `get_all_signals()` - ~100 lines
**File:** `argo/argo/api/signals.py` (lines 121-220)

### Current Issues:
- Handles multiple responsibilities: rate limiting, input sanitization, filtering, pagination, response building
- Complex nested conditionals for filtering
- Mixed concerns (authentication, validation, data processing, response formatting)

### Refactoring Suggestions:

```python
@router.get("", response_model=PaginatedResponse)
async def get_all_signals(
    request: Request,
    response: Response,
    limit: int = Query(10, ge=1, le=100, description="Number of signals to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    premium_only: bool = Query(False, description="Filter premium signals only"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    action: Optional[str] = Query(None, description="Filter by action (BUY/SELL)"),
    authorization: Optional[str] = Header(None)
):
    """Get all signals with pagination and filtering"""
    # Rate limiting
    client_id = _get_client_id(request)
    _check_rate_limit(client_id)
    
    # Input sanitization
    sanitized_params = _sanitize_input_params(symbol, action)
    
    # Filter and paginate
    filtered_signals = _filter_signals(sanitized_params, premium_only)
    paginated_result = _paginate_signals(filtered_signals, limit, offset)
    
    # Add rate limit headers
    _add_rate_limit_headers(response, client_id)
    
    return paginated_result

def _get_client_id(request: Request) -> str:
    """Extract client ID from request"""
    return request.client.host if request.client else "anonymous"

def _check_rate_limit(client_id: str):
    """Check and enforce rate limiting"""
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per minute."
        )

def _sanitize_input_params(symbol: Optional[str], action: Optional[str]) -> Dict:
    """Sanitize and validate input parameters"""
    sanitized = {}
    
    if symbol:
        symbol = symbol.upper().strip()
        if not re.match(r'^[A-Z0-9_-]+$', symbol) or len(symbol) > 20:
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        sanitized['symbol'] = symbol
    
    if action:
        action = action.upper().strip()
        if action not in ["BUY", "SELL"]:
            raise HTTPException(status_code=400, detail="Invalid action. Must be BUY or SELL")
        sanitized['action'] = action
    
    return sanitized

def _filter_signals(sanitized_params: Dict, premium_only: bool) -> List:
    """Filter signals based on criteria"""
    filtered = SIGNALS_DB.copy()
    
    if premium_only:
        filtered = [s for s in filtered if s.get("confidence", 0) >= 95]
    
    if sanitized_params.get('symbol'):
        filtered = [s for s in filtered if s.get("symbol") == sanitized_params['symbol']]
    
    if sanitized_params.get('action'):
        filtered = [s for s in filtered if s.get("action") == sanitized_params['action']]
    
    return filtered

def _paginate_signals(filtered_signals: List, limit: int, offset: int) -> PaginatedResponse:
    """Paginate filtered signals"""
    total = len(filtered_signals)
    paginated = filtered_signals[offset:offset + limit]
    
    return PaginatedResponse(
        items=[SignalResponse(**s) for s in paginated],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )

def _add_rate_limit_headers(response: Response, client_id: str):
    """Add rate limit headers to response"""
    remaining = max(0, RATE_LIMIT_MAX - len(rate_limit_store.get(client_id, [])))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
```

### Benefits:
- **Single Responsibility**: Each function has one clear purpose
- **Testability**: Each helper function can be tested independently
- **Readability**: Main function reads like a high-level workflow
- **Maintainability**: Changes to filtering logic are isolated

---

## 2. `run_backtest()` - ~82 lines
**File:** `argo/argo/backtest/strategy_backtester.py` (lines 37-118)

### Current Issues:
- Handles multiple responsibilities: data fetching, validation, filtering, simulation loop, metrics calculation
- Complex nested logic for position management
- Mixed concerns (data management, signal generation, position tracking, metrics)

### Refactoring Suggestions:

```python
async def run_backtest(
    self,
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_confidence: float = 75.0
) -> Optional[BacktestMetrics]:
    """Run backtest for signal generation strategy"""
    # Step 1: Prepare data
    df = self._prepare_backtest_data(symbol, start_date, end_date)
    if df is None:
        return None
    
    # Step 2: Reset state
    self.reset()
    
    # Step 3: Run simulation
    self._run_simulation_loop(df, symbol, min_confidence)
    
    # Step 4: Close remaining positions
    self._close_remaining_positions(df, symbol)
    
    # Step 5: Calculate metrics
    return self.calculate_metrics()

def _prepare_backtest_data(
    self, 
    symbol: str, 
    start_date: Optional[datetime], 
    end_date: Optional[datetime]
) -> Optional[pd.DataFrame]:
    """Fetch, validate, and filter historical data"""
    df = self.data_manager.fetch_historical_data(symbol, period="5y")
    if df is None or df.empty:
        logger.error(f"No data available for {symbol}")
        return None
    
    # Validate data
    is_valid, issues = self.data_manager.validate_data(df)
    if not is_valid:
        logger.error(f"Data validation failed: {issues}")
        return None
    
    # Filter by date range
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    if len(df) < 100:
        logger.error(f"Insufficient data: {len(df)} rows")
        return None
    
    logger.info(f"Running strategy backtest for {symbol}: {len(df)} rows")
    return df

def _run_simulation_loop(self, df: pd.DataFrame, symbol: str, min_confidence: float):
    """Run the main simulation loop"""
    for i in range(200, len(df)):  # Start after warmup period
        current_date = df.index[i]
        current_price = df.iloc[i]['Close']
        
        # Generate signal
        signal = await self._generate_historical_signal(symbol, df, i, current_price)
        
        # Process signal
        if signal and signal.get('confidence', 0) >= min_confidence:
            self._process_signal(symbol, current_price, current_date, signal)
        
        # Check exit conditions
        if symbol in self.positions:
            self._check_exit_conditions(symbol, current_price, current_date)
        
        # Update equity
        self.update_equity(current_price, current_date)

def _process_signal(
    self, 
    symbol: str, 
    current_price: float, 
    current_date: datetime, 
    signal: Dict
):
    """Process signal and enter/exit positions"""
    action = signal.get('action', 'HOLD')
    
    if action == 'BUY' and symbol not in self.positions:
        self._enter_position(symbol, current_price, current_date, signal, 'LONG')
    elif action == 'SELL' and symbol in self.positions:
        self._exit_position(symbol, current_price, current_date)

def _close_remaining_positions(self, df: pd.DataFrame, symbol: str):
    """Close any remaining positions at end of backtest"""
    if symbol in self.positions:
        final_price = df.iloc[-1]['Close']
        self._exit_position(symbol, final_price, df.index[-1])
```

### Benefits:
- **Single Responsibility**: Each function handles one aspect of backtesting
- **Testability**: Data preparation, simulation, and position management can be tested separately
- **Readability**: Main function shows the high-level workflow clearly
- **Maintainability**: Changes to simulation logic are isolated from data preparation

---

## Summary

### Total Functions Found: 2

1. **API Layer** (`argo/argo/api/signals.py`):
   - `get_all_signals()` - ~100 lines

2. **Backtest Layer** (`argo/argo/backtest/strategy_backtester.py`):
   - `run_backtest()` - ~82 lines

### Refactoring Priority:
- **High**: Both functions handle multiple responsibilities and would benefit significantly from refactoring
- **Impact**: Improved testability, maintainability, and code clarity

### Next Steps:
1. Refactor `get_all_signals()` to separate concerns
2. Refactor `run_backtest()` to improve modularity
3. Add unit tests for extracted helper functions
4. Verify all tests pass after refactoring

