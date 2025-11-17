# Refactoring Analysis: Functions Over 50 Lines in argo/argo/core/

## Summary

Found **8 functions** over 50 lines that should be refactored for better maintainability, testability, and readability.

---

## 1. `SignalTracker.log_signal()` - 58 lines
**File:** `signal_tracker.py` (lines 104-162)

### Current Issues:
- Handles multiple responsibilities: signal preparation, database insertion, file logging, metrics
- Complex nested try-except blocks
- Mixed concerns (validation, hashing, persistence, metrics)

### Refactoring Suggestions:

```python
def log_signal(self, signal):
    """Log signal with latency tracking and server timestamp"""
    start_time = time.time()
    
    with self._lock:
        signal = self._prepare_signal(signal, start_time)
        self._persist_signal(signal)
        self._log_to_file(signal)
        self._record_metrics(start_time)
        
    return signal['signal_id']

def _prepare_signal(self, signal, start_time):
    """Prepare signal with ID, timestamp, and hash"""
    if 'signal_id' not in signal:
        signal['signal_id'] = self._generate_signal_id()
    if 'timestamp' not in signal:
        signal['timestamp'] = datetime.utcnow().isoformat()
    
    signal['server_timestamp'] = start_time
    signal['sha256'] = self._calculate_sha256(signal)
    
    generation_latency_ms = int((time.time() - start_time) * 1000)
    signal['generation_latency_ms'] = generation_latency_ms
    
    return signal

def _persist_signal(self, signal):
    """Persist signal to database"""
    conn = sqlite3.connect(str(self.db_file))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''INSERT INTO signals (...) VALUES (...)''', (...))
        conn.commit()
        logger.info(f"✅ Signal logged: {signal['signal_id']} - {signal['symbol']}")
    except sqlite3.IntegrityError:
        logger.warning(f"Signal {signal['signal_id']} already exists")
    finally:
        conn.close()

def _log_to_file(self, signal):
    """Write signal to log file"""
    with self.signals_log.open('a') as f:
        f.write(json.dumps(signal, sort_keys=True) + '\n')

def _record_metrics(self, start_time):
    """Record Prometheus metrics if available"""
    try:
        from argo.core.metrics import signal_generation_latency
        signal_generation_latency.observe(time.time() - start_time)
    except (ImportError, AttributeError):
        pass
```

**Benefits:**
- Single Responsibility Principle: Each method has one clear purpose
- Easier to test individual components
- Better error isolation
- Improved readability

---

## 2. `SignalGenerationService.__init__()` - 81 lines
**File:** `signal_generation_service.py` (lines 67-148)

### Current Issues:
- Initializes too many components in one method
- Complex conditional logic for environment detection
- Mixed initialization concerns (config, data sources, trading engine)

### Refactoring Suggestions:

```python
def __init__(self):
    self.tracker = SignalTracker()
    self._init_consensus_engine()
    self._init_environment()
    self._init_data_sources()
    self._init_trading_engine()
    self._init_performance_tracking()
    logger.info("✅ Signal Generation Service initialized")

def _init_consensus_engine(self):
    """Initialize consensus engine with config"""
    try:
        self.consensus_engine = WeightedConsensusEngine()
        self.trading_config = self.consensus_engine.config.get('trading', {})
    except Exception as e:
        logger.warning(f"⚠️  Could not load consensus engine config: {e}")
        self._init_fallback_consensus_engine()
        self.trading_config = {}

def _init_fallback_consensus_engine(self):
    """Initialize fallback consensus engine with defaults"""
    self.consensus_engine = WeightedConsensusEngine.__new__(WeightedConsensusEngine)
    self.consensus_engine.weights = {
        'massive': 0.40, 'alpha_vantage': 0.25,
        'x_sentiment': 0.20, 'sonar': 0.15
    }
    self.consensus_engine.calculate_consensus = lambda signals: self._simple_consensus(signals)

def _init_environment(self):
    """Initialize environment detection and cursor awareness"""
    from argo.core.environment import detect_environment, get_environment_info
    self.environment = detect_environment()
    env_info = get_environment_info()
    logger.info(f"🌍 Signal Generation Service - Environment: {self.environment}")
    logger.debug(f"   Environment details: {env_info}")
    
    self._cursor_aware = (self.environment == 'development')
    if self._cursor_aware:
        logger.info("💡 Development mode: Trading will pause when Cursor is closed or computer is asleep")

def _init_trading_engine(self):
    """Initialize trading engine if auto-execution is enabled"""
    self.auto_execute = self.trading_config.get('auto_execute', False)
    self.trading_engine = None
    self._positions_cache = None
    self._positions_cache_time = None
    self._positions_cache_ttl = 30
    
    if not self.auto_execute:
        return
    
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        self.trading_engine = PaperTradingEngine()
        self._validate_trading_engine()
    except Exception as e:
        logger.warning(f"⚠️  Trading engine not available: {e}")
        self.auto_execute = False

def _init_performance_tracking(self):
    """Initialize performance tracking"""
    self._performance_tracker = None
    self._peak_equity = None
    self._daily_start_equity = None
    self._daily_loss_limit_pct = self.trading_config.get('daily_loss_limit_pct', 5.0)
    self._trading_paused = False
    
    try:
        from argo.tracking.unified_tracker import UnifiedPerformanceTracker
        self._performance_tracker = UnifiedPerformanceTracker()
    except Exception as e:
        logger.debug(f"Performance tracker not available: {e}")
```

**Benefits:**
- Clear separation of initialization concerns
- Easier to test individual initialization steps
- Better error handling per component
- More maintainable configuration

---

## 3. `SignalGenerationService._init_data_sources()` - 173 lines
**File:** `signal_generation_service.py` (lines 189-362)

### Current Issues:
- Extremely long method with repetitive initialization patterns
- Complex API key resolution logic (AWS Secrets Manager → env vars → config.json)
- Each data source initialization is similar but duplicated

### Refactoring Suggestions:

```python
def _init_data_sources(self):
    """Initialize all data sources with API keys from multiple sources"""
    self.data_sources = {}
    
    try:
        config_api_keys = self._load_config_api_keys()
        get_secret = self._get_secrets_manager()
        
        # Initialize each data source using a factory pattern
        source_configs = [
            {
                'name': 'massive',
                'class': MassiveDataSource,
                'secret_keys': ['polygon-api-key'],
                'env_keys': ['POLYGON_API_KEY'],
                'config_key': 'massive',
                'validator': self._validate_massive_key
            },
            {
                'name': 'alpha_vantage',
                'class': AlphaVantageDataSource,
                'secret_keys': ['alpha-vantage-api-key'],
                'env_keys': ['ALPHA_VANTAGE_API_KEY'],
                'config_key': 'alpha_vantage'
            },
            # ... similar configs for other sources
        ]
        
        for config in source_configs:
            self._init_data_source(config, get_secret, config_api_keys)
        
        self._log_data_source_summary()
        
    except Exception as e:
        logger.error(f"❌ Error initializing data sources: {e}")

def _load_config_api_keys(self) -> Dict[str, str]:
    """Load API keys from config.json"""
    config_api_keys = {}
    config_path = self._find_config_path()
    
    if not config_path:
        logger.warning("⚠️  No config.json found in any expected path")
        return config_api_keys
    
    try:
        with open(config_path) as f:
            config = json.load(f)
            config_api_keys = {
                'massive': config.get('massive', {}).get('api_key'),
                'alpha_vantage': config.get('alpha_vantage', {}).get('api_key'),
                'xai': config.get('xai', {}).get('api_key') or config.get('x_api', {}).get('bearer_token'),
                'sonar': config.get('sonar', {}).get('api_key')
            }
            logger.debug(f"Loaded API keys from {config_path}: {list(config_api_keys.keys())}")
    except Exception as e:
        logger.warning(f"⚠️  Could not load API keys from config.json: {e}")
    
    return config_api_keys

def _get_secrets_manager(self):
    """Get secrets manager function if available"""
    try:
        from argo.utils.secrets_manager import get_secret
        return get_secret
    except ImportError:
        return None

def _init_data_source(self, config: Dict, get_secret, config_api_keys: Dict):
    """Initialize a single data source using configuration"""
    api_key = self._resolve_api_key(
        config['name'],
        config.get('secret_keys', []),
        config.get('env_keys', []),
        config.get('config_key'),
        get_secret,
        config_api_keys,
        config.get('validator')
    )
    
    if not api_key:
        logger.warning(f"⚠️  {config['name']} API key not found")
        return
    
    try:
        self.data_sources[config['name']] = config['class'](api_key)
        logger.info(f"✅ {config['name']} data source initialized")
    except Exception as e:
        logger.warning(f"⚠️  {config['name']} init error: {e}")

def _resolve_api_key(self, source_name: str, secret_keys: List[str], 
                     env_keys: List[str], config_key: str, 
                     get_secret, config_api_keys: Dict, 
                     validator=None) -> Optional[str]:
    """Resolve API key from multiple sources (AWS Secrets → env → config)"""
    # Try AWS Secrets Manager first
    if get_secret:
        for secret_key in secret_keys:
            api_key = get_secret(secret_key, service="argo")
            if api_key:
                logger.debug(f"{source_name} API key found in AWS Secrets Manager")
                return api_key
    
    # Try environment variables
    for env_key in env_keys:
        api_key = os.getenv(env_key)
        if api_key:
            logger.debug(f"{source_name} API key found in environment variable")
            return api_key
    
    # Try config.json
    if config_key and config_key in config_api_keys:
        api_key = config_api_keys[config_key]
        if api_key:
            if validator:
                api_key = validator(api_key)
            if api_key:
                logger.info(f"✅ {source_name} API key found in config.json")
                return api_key
    
    return None

def _validate_massive_key(self, api_key: str) -> Optional[str]:
    """Validate Massive.com API key format"""
    key_len = len(api_key)
    has_dash = '-' in api_key
    
    if has_dash or key_len > 40:
        logger.warning("⚠️  Config has S3 access key, not Massive.com REST API key.")
        logger.warning("   Get your REST API key from: https://massive.com/dashboard")
        return None
    
    return api_key
```

**Benefits:**
- DRY principle: Eliminates code duplication
- Factory pattern makes adding new data sources easier
- Centralized API key resolution logic
- Better testability with smaller, focused methods

---

## 4. `SignalGenerationService.generate_signal_for_symbol()` - 224 lines
**File:** `signal_generation_service.py` (lines 364-588)

### Current Issues:
- Extremely long method handling multiple steps
- Complex nested conditionals for data source priority
- Mixed concerns: data fetching, consensus calculation, signal building

### Refactoring Suggestions:

```python
async def generate_signal_for_symbol(self, symbol: str) -> Optional[Dict]:
    """Generate a signal for a single symbol using weighted consensus"""
    try:
        # Step 1: Fetch signals from all sources
        source_signals = await self._fetch_all_source_signals(symbol)
        
        if not source_signals:
            logger.info(f"ℹ️  No source signals for {symbol} - all sources failed")
            return None
        
        # Step 2: Calculate weighted consensus
        consensus = self._calculate_consensus(source_signals, symbol)
        if not consensus or consensus['confidence'] < 75.0:
            return None
        
        # Step 3: Apply regime detection and adjust confidence
        consensus = self._apply_regime_adjustment(consensus, symbol)
        
        # Step 4: Build final signal
        signal = self._build_signal(symbol, consensus, source_signals)
        
        # Step 5: Generate AI reasoning
        signal['reasoning'] = self._generate_reasoning(signal, consensus)
        
        return signal
        
    except Exception as e:
        logger.error(f"❌ Error generating signal for {symbol}: {e}")
        return None

async def _fetch_all_source_signals(self, symbol: str) -> Dict[str, Dict]:
    """Fetch signals from all available data sources"""
    source_signals = {}
    
    # Market data sources (priority: Alpaca Pro → Massive.com)
    await self._fetch_market_data_signals(symbol, source_signals)
    
    # Technical indicator sources (priority: yfinance → Alpha Vantage)
    await self._fetch_technical_indicator_signals(symbol, source_signals)
    
    # Sentiment sources
    await self._fetch_sentiment_signals(symbol, source_signals)
    
    # AI analysis sources
    await self._fetch_ai_analysis_signals(symbol, source_signals)
    
    return source_signals

async def _fetch_market_data_signals(self, symbol: str, source_signals: Dict):
    """Fetch market data signals with fallback priority"""
    # Try Alpaca Pro first
    if 'alpaca_pro' in self.data_sources:
        signal = await self._try_fetch_signal('alpaca_pro', symbol, 'fetch_price_data')
        if signal:
            source_signals['alpaca_pro'] = signal
            return
    
    # Fallback to Massive.com
    if 'massive' in self.data_sources:
        signal = await self._try_fetch_signal('massive', symbol, 'fetch_price_data')
        if signal:
            source_signals['massive'] = signal

async def _fetch_technical_indicator_signals(self, symbol: str, source_signals: Dict):
    """Fetch technical indicator signals with smart fallback"""
    yfinance_signal = None
    yfinance_exception = False
    
    # Try yfinance first
    if 'yfinance' in self.data_sources:
        try:
            indicators = self.data_sources['yfinance'].fetch_technical_indicators(symbol)
            if indicators:
                yfinance_signal = self.data_sources['yfinance'].generate_signal(indicators, symbol)
                if yfinance_signal:
                    source_signals['yfinance'] = yfinance_signal
        except Exception as e:
            yfinance_exception = True
            logger.debug(f"yfinance error for {symbol}: {e}")
    
    # Use Alpha Vantage only if yfinance failed (not if it returned None due to low confidence)
    if 'alpha_vantage' in self.data_sources and (not yfinance_signal and yfinance_exception):
        signal = await self._try_fetch_signal('alpha_vantage', symbol, 'fetch_technical_indicators')
        if signal:
            source_signals['alpha_vantage'] = signal

async def _try_fetch_signal(self, source_name: str, symbol: str, method_name: str) -> Optional[Dict]:
    """Generic method to try fetching a signal from a data source"""
    try:
        source = self.data_sources[source_name]
        if method_name == 'fetch_price_data':
            df = await source.fetch_price_data(symbol, days=90)
            if df is not None and len(df) > 0:
                signal = source.generate_signal(df, symbol)
                if signal:
                    logger.info(f"✅ {source_name} signal for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%")
                    return signal
        elif method_name == 'fetch_technical_indicators':
            indicators = source.fetch_technical_indicators(symbol)
            if indicators:
                signal = source.generate_signal(indicators, symbol)
                if signal:
                    logger.info(f"✅ {source_name} signal for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%")
                    return signal
    except Exception as e:
        logger.debug(f"{source_name} error for {symbol}: {e}")
    return None

def _calculate_consensus(self, source_signals: Dict, symbol: str) -> Optional[Dict]:
    """Calculate weighted consensus from source signals"""
    logger.info(f"📊 Source signals for {symbol}: {[(s, sig.get('direction'), f'{sig.get('confidence')}%') for s, sig in source_signals.items()]}")
    
    consensus_input = {
        source: {
            'direction': signal.get('direction', 'NEUTRAL'),
            'confidence': signal.get('confidence', 0) / 100.0
        }
        for source, signal in source_signals.items()
    }
    
    consensus = self.consensus_engine.calculate_consensus(consensus_input)
    
    if consensus:
        logger.info(f"📈 Consensus for {symbol}: {consensus.get('direction')} @ {consensus.get('confidence')}% (threshold: 75%)")
    
    return consensus

def _apply_regime_adjustment(self, consensus: Dict, symbol: str) -> Dict:
    """Apply market regime detection and adjust confidence"""
    regime = 'UNKNOWN'
    if 'massive' in self.data_sources:
        try:
            df = await self.data_sources['massive'].fetch_price_data(symbol, days=200)
            if df is not None:
                regime = detect_regime(df)
                consensus['confidence'] = adjust_confidence(consensus['confidence'], regime)
        except Exception as e:
            logger.debug(f"Regime detection error: {e}")
    
    consensus['regime'] = regime
    return consensus

def _build_signal(self, symbol: str, consensus: Dict, source_signals: Dict) -> Dict:
    """Build final signal dictionary"""
    direction = consensus['direction']
    action = "BUY" if direction == "LONG" else "SELL"
    
    entry_price = self._get_entry_price(source_signals, symbol)
    stop_loss, take_profit = self._calculate_stop_and_target(entry_price, action)
    
    return {
        'symbol': symbol,
        'action': action,
        'entry_price': round(entry_price, 2),
        'target_price': round(take_profit, 2),
        'stop_price': round(stop_loss, 2),
        'confidence': round(consensus['confidence'], 2),
        'strategy': 'weighted_consensus_v6',
        'asset_type': 'crypto' if '-USD' in symbol else 'stock',
        'data_source': 'weighted_consensus',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'regime': consensus.get('regime', 'UNKNOWN'),
        'consensus_agreement': consensus.get('agreement', 0),
        'sources_count': consensus.get('sources', 0)
    }

def _get_entry_price(self, source_signals: Dict, symbol: str) -> float:
    """Get entry price from primary source or fallback"""
    if 'massive' in source_signals:
        return source_signals['massive'].get('entry_price')
    elif 'alpha_vantage' in source_signals:
        return source_signals['alpha_vantage'].get('indicators', {}).get('current_price')
    
    # Fallback to defaults
    price_defaults = {
        "AAPL": 175.0, "NVDA": 460.0, "TSLA": 260.0, "MSFT": 161.0,
        "BTC-USD": 40000.0, "ETH-USD": 2500.0
    }
    return price_defaults.get(symbol, 100.0)

def _calculate_stop_and_target(self, entry_price: float, action: str) -> Tuple[float, float]:
    """Calculate stop loss and take profit prices"""
    stop_loss_pct = self.trading_config.get('stop_loss', 0.03)
    profit_target_pct = self.trading_config.get('profit_target', 0.05)
    
    if action == "BUY":
        stop_loss = entry_price * (1 - stop_loss_pct)
        take_profit = entry_price * (1 + profit_target_pct)
    else:  # SELL
        stop_loss = entry_price * (1 + stop_loss_pct)
        take_profit = entry_price * (1 - profit_target_pct)
    
    return stop_loss, take_profit
```

**Benefits:**
- Clear separation of concerns (fetching, consensus, building)
- Easier to test each step independently
- Better error handling per step
- More maintainable and readable

---

## 5. `SignalGenerationService.generate_signals_cycle()` - 103 lines
**File:** `signal_generation_service.py` (lines 713-816)

### Current Issues:
- Handles signal generation, validation, and trade execution in one method
- Complex nested conditionals
- Mixed responsibilities

### Refactoring Suggestions:

```python
async def generate_signals_cycle(self, symbols: List[str] = None) -> List[Dict]:
    """Generate signals for all symbols in one cycle with optimized trading execution"""
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    
    generated_signals = []
    account, existing_positions = self._get_trading_context()
    
    for symbol in symbols:
        try:
            signal = await self.generate_signal_for_symbol(symbol)
            if not signal:
                continue
            
            # Store signal in database
            signal_id = self.tracker.log_signal(signal)
            signal['signal_id'] = signal_id
            generated_signals.append(signal)
            logger.info(f"✅ Generated signal: {symbol} {signal['action']} @ ${signal['entry_price']} ({signal['confidence']}% confidence)")
            
            # Execute trade if enabled
            if self.auto_execute and self.trading_engine and account and not self._paused:
                await self._execute_trade_if_valid(signal, account, existing_positions)
                
        except Exception as e:
            logger.error(f"❌ Error in signal cycle for {symbol}: {e}")
    
    return generated_signals

def _get_trading_context(self) -> Tuple[Optional[Dict], List[Dict]]:
    """Get account and positions for trading context"""
    if not (self.auto_execute and self.trading_engine):
        return None, []
    
    account = self.trading_engine.get_account_details()
    existing_positions = self._get_cached_positions()
    return account, existing_positions

async def _execute_trade_if_valid(self, signal: Dict, account: Dict, existing_positions: List[Dict]):
    """Execute trade if all validations pass"""
    try:
        # Risk validation
        can_trade, reason = self._validate_trade(signal, account)
        if not can_trade:
            logger.warning(f"⏭️  Skipping {signal['symbol']} - {reason}")
            return
        
        # Check existing position
        if any(p['symbol'] == signal['symbol'] for p in existing_positions):
            logger.info(f"⏭️  Skipping {signal['symbol']} - position already exists")
            return
        
        # Check correlation limits
        if not self._check_correlation_groups(signal['symbol'], existing_positions):
            return
        
        # Execute trade
        order_id = self.trading_engine.execute_signal(signal)
        if order_id:
            await self._handle_successful_trade(signal, order_id, existing_positions)
        else:
            logger.warning(f"⚠️  Trade execution returned no order ID for {signal['symbol']}")
            
    except Exception as e:
        logger.error(f"❌ Error executing trade for {signal['symbol']}: {e}")

async def _handle_successful_trade(self, signal: Dict, order_id: str, existing_positions: List[Dict]):
    """Handle successful trade execution"""
    signal['order_id'] = str(order_id)
    
    # Get order status
    order_status = self.trading_engine.get_order_status(order_id)
    if order_status:
        signal['order_status'] = order_status.get('status')
        signal['filled_qty'] = order_status.get('filled_qty', 0)
        signal['filled_price'] = order_status.get('filled_avg_price')
    
    # Record in performance tracker
    self._record_trade_in_tracker(signal, order_id)
    
    # Journal trade
    self._journal_trade(signal, order_id, order_status)
    
    # Update position cache
    self._update_position_cache(signal, existing_positions)
    
    logger.info(f"✅ Trade executed: {signal['symbol']} {signal['action']} - Order ID: {order_id}")

def _record_trade_in_tracker(self, signal: Dict, order_id: str):
    """Record trade in performance tracker"""
    if not self._performance_tracker:
        return
    
    try:
        trade = self._performance_tracker.record_signal_entry(
            signal_id=str(signal.get('signal_id', '')),
            asset_class='stock' if not signal['symbol'].endswith('-USD') else 'crypto',
            symbol=signal['symbol'],
            signal_type='long' if signal['action'] == 'BUY' else 'short',
            entry_price=signal['entry_price'],
            quantity=signal.get('filled_qty', 0) or signal.get('qty', 0),
            confidence=signal['confidence'],
            alpaca_order_id=str(order_id)
        )
        signal['trade_id'] = trade.id
        logger.debug(f"📊 Trade recorded: {trade.id}")
    except Exception as e:
        logger.warning(f"Could not record trade in tracker: {e}")

def _update_position_cache(self, signal: Dict, existing_positions: List[Dict]):
    """Update position cache after successful trade"""
    self._positions_cache = None
    self._positions_cache_time = None
    
    existing_positions.append({
        'symbol': signal['symbol'],
        'side': signal['action'],
        'qty': signal.get('filled_qty', 0) or 0,
        'entry_price': signal.get('filled_price') or signal['entry_price'],
        'stop_price': signal.get('stop_price'),
        'target_price': signal.get('target_price')
    })
```

**Benefits:**
- Clear separation between signal generation and trade execution
- Easier to test trade execution logic separately
- Better error handling
- More maintainable

---

## 6. `SignalGenerationService.start_background_generation()` - 65 lines
**File:** `signal_generation_service.py` (lines 948-1013)

### Current Issues:
- Handles pause checking, signal generation, and timing in one method
- Complex pause state management

### Refactoring Suggestions:

```python
async def start_background_generation(self, interval_seconds: int = 5):
    """Start background signal generation task with position monitoring"""
    self.running = True
    logger.info(f"🚀 Starting background signal generation (every {interval_seconds} seconds)")
    
    self._start_position_monitoring()
    
    pause_checker = PauseStateChecker(self, interval_seconds=30)
    
    while self.running:
        try:
            # Check and update pause state
            pause_checker.check_and_update()
            
            # Skip if paused
            if self._paused:
                await asyncio.sleep(interval_seconds)
                continue
            
            # Generate signals
            await self._run_signal_generation_cycle(interval_seconds)
            
        except Exception as e:
            logger.error(f"❌ Error in background generation cycle: {e}")
            await asyncio.sleep(interval_seconds)

def _start_position_monitoring(self):
    """Start position monitoring task if enabled"""
    if self.trading_config.get('enable_position_monitoring', True) and self.auto_execute:
        import asyncio
        asyncio.create_task(self.monitor_positions())
        logger.info("🔄 Position monitoring started")

async def _run_signal_generation_cycle(self, interval_seconds: int):
    """Run one signal generation cycle"""
    start_time = datetime.now(timezone.utc)
    signals = await self.generate_signals_cycle()
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info(f"📊 Generated {len(signals)} signals in {elapsed:.2f}s")
    await asyncio.sleep(interval_seconds)

class PauseStateChecker:
    """Manages pause state checking for development mode"""
    def __init__(self, service, interval_seconds=30):
        self.service = service
        self.interval_seconds = interval_seconds
        self.last_check = datetime.now(timezone.utc)
    
    def check_and_update(self):
        """Check if pause state should be updated"""
        if not self.service._cursor_aware:
            return
        
        time_since_check = (datetime.now(timezone.utc) - self.last_check).total_seconds()
        if time_since_check < self.interval_seconds:
            return
        
        should_pause = self.service._should_pause_trading()
        self._update_pause_state(should_pause)
        self.last_check = datetime.now(timezone.utc)
    
    def _update_pause_state(self, should_pause: bool):
        """Update pause state and log appropriately"""
        if should_pause and not self.service._paused:
            self.service._paused = True
            reason = "Cursor is not running" if not self.service._is_cursor_running() else "Computer appears to be asleep"
            logger.info(f"💤 {reason} - pausing signal generation and trading")
            logger.info("   Trading will resume automatically when Cursor starts or computer wakes")
        elif not should_pause and self.service._paused:
            self.service._paused = False
            reason = "Cursor detected" if not self.service._is_cursor_running() else "Computer awake"
            logger.info(f"✅ Resuming signal generation and trading ({reason})")
```

**Benefits:**
- Separates pause state management into its own class
- Cleaner main loop
- Easier to test pause logic
- Better separation of concerns

---

## 7. `PaperTradingEngine.__init__()` - 138 lines
**File:** `paper_trading_engine.py` (lines 31-169)

### Current Issues:
- Complex credential resolution from multiple sources
- Mixed initialization concerns

### Refactoring Suggestions:

```python
def __init__(self, config_path=None):
    self._init_environment()
    self._init_config(config_path)
    credentials = self._resolve_credentials()
    self._init_alpaca_client(credentials)

def _init_environment(self):
    """Initialize environment detection"""
    from argo.core.environment import detect_environment, get_environment_info
    self.environment = detect_environment()
    env_info = get_environment_info()
    logger.info(f"🌍 Environment detected: {self.environment}")
    logger.debug(f"   Environment details: {env_info}")

def _init_config(self, config_path):
    """Initialize configuration"""
    self.config = {}
    config_path = self._find_config_path(config_path)
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                self.config = config.get('trading', {})
        except Exception as e:
            logger.warning(f"Failed to load config.json: {e}")

def _resolve_credentials(self) -> Dict[str, Optional[str]]:
    """Resolve Alpaca credentials from multiple sources"""
    credentials = {
        'api_key': None,
        'secret_key': None,
        'paper': True,
        'account_name': None
    }
    
    # Try AWS Secrets Manager first
    if SECRETS_MANAGER_AVAILABLE:
        credentials.update(self._get_credentials_from_secrets_manager())
    
    # Fallback to config.json
    if not credentials['api_key'] or not credentials['secret_key']:
        config_creds = self._get_credentials_from_config()
        credentials['api_key'] = credentials['api_key'] or config_creds['api_key']
        credentials['secret_key'] = credentials['secret_key'] or config_creds['secret_key']
        credentials['account_name'] = credentials['account_name'] or config_creds['account_name']
    
    # Final fallback to environment variables
    credentials['api_key'] = credentials['api_key'] or os.getenv('ALPACA_API_KEY')
    credentials['secret_key'] = credentials['secret_key'] or os.getenv('ALPACA_SECRET_KEY')
    
    credentials['account_name'] = credentials['account_name'] or f"{self.environment.title()} Account"
    
    return credentials

def _get_credentials_from_secrets_manager(self) -> Dict[str, Optional[str]]:
    """Get credentials from AWS Secrets Manager"""
    credentials = {'api_key': None, 'secret_key': None, 'paper': True}
    
    try:
        service = "argo"
        if self.environment == "development":
            credentials['api_key'] = get_secret("alpaca-api-key-dev", service=service) or \
                                   get_secret("alpaca-api-key", service=service)
            credentials['secret_key'] = get_secret("alpaca-secret-key-dev", service=service) or \
                                      get_secret("alpaca-secret-key", service=service)
        else:
            credentials['api_key'] = get_secret("alpaca-api-key-production", service=service) or \
                                   get_secret("alpaca-api-key", service=service)
            credentials['secret_key'] = get_secret("alpaca-secret-key-production", service=service) or \
                                      get_secret("alpaca-secret-key", service=service)
        
        paper_mode = get_secret("alpaca-paper", service=service, default="true")
        credentials['paper'] = paper_mode.lower() == "true" if paper_mode else True
    except Exception as e:
        logger.warning(f"Failed to get Alpaca credentials from AWS Secrets Manager: {e}")
    
    return credentials

def _get_credentials_from_config(self) -> Dict[str, Optional[str]]:
    """Get credentials from config.json"""
    credentials = {'api_key': None, 'secret_key': None, 'account_name': None}
    
    config_path = self._find_config_path(None)
    if not config_path or not os.path.exists(config_path):
        return credentials
    
    try:
        with open(config_path) as f:
            config = json.load(f)
            alpaca_config = config.get('alpaca', {})
            
            if isinstance(alpaca_config, dict):
                if self.environment == "production" and "production" in alpaca_config:
                    env_config = alpaca_config["production"]
                    credentials.update({
                        'api_key': env_config.get('api_key'),
                        'secret_key': env_config.get('secret_key'),
                        'account_name': env_config.get('account_name', 'Production Trading Account')
                    })
                elif self.environment == "development" and "dev" in alpaca_config:
                    env_config = alpaca_config["dev"]
                    credentials.update({
                        'api_key': env_config.get('api_key'),
                        'secret_key': env_config.get('secret_key'),
                        'account_name': env_config.get('account_name', 'Dev Trading Account')
                    })
    except Exception as e:
        logger.warning(f"Failed to load credentials from config.json: {e}")
    
    return credentials

def _init_alpaca_client(self, credentials: Dict):
    """Initialize Alpaca trading client"""
    if not (ALPACA_AVAILABLE and credentials['api_key'] and credentials['secret_key']):
        logger.warning("Alpaca not configured - simulation mode")
        self.alpaca_enabled = False
        self._order_tracker = {}
        self._retry_attempts = 3
        self._retry_delay = 1
        return
    
    try:
        self.alpaca = TradingClient(
            credentials['api_key'],
            credentials['secret_key'],
            paper=credentials['paper']
        )
        account = self.alpaca.get_account()
        self.account_name = credentials['account_name']
        logger.info(f"✅ Alpaca connected ({self.environment}) | Account: {self.account_name}")
        logger.info(f"   Portfolio: ${float(account.portfolio_value):,.2f} | Buying Power: ${float(account.buying_power):,.2f}")
        self.alpaca_enabled = True
        self._order_tracker = {}
        self._retry_attempts = self.config.get('max_retry_attempts', 3)
        self._retry_delay = self.config.get('retry_delay_seconds', 1)
    except Exception as e:
        logger.error(f"Alpaca connection failed: {e}")
        self.alpaca_enabled = False
```

**Benefits:**
- Clear separation of credential resolution steps
- Easier to test each resolution method
- Better error handling
- More maintainable

---

## 8. `PaperTradingEngine._execute_live()` - 174 lines
**File:** `paper_trading_engine.py` (lines 227-401)

### Current Issues:
- Extremely long method handling order creation, position sizing, and bracket orders
- Complex conditional logic for BUY vs SELL
- Mixed concerns

### Refactoring Suggestions:

```python
def _execute_live(self, signal):
    """Execute live trade through Alpaca"""
    try:
        symbol, action = signal['symbol'], signal['action']
        
        if not self._is_trade_allowed(symbol):
            return None
        
        account = self.alpaca.get_account()
        
        # Determine order details
        order_details = self._prepare_order_details(signal, account, action)
        if not order_details:
            return None
        
        # Submit main order
        order = self._submit_main_order(order_details)
        if not order:
            return None
        
        # Track order
        self._track_order(order, signal, order_details)
        
        # Place bracket orders (stop loss and take profit)
        if order_details.get('place_bracket'):
            self._place_bracket_orders(symbol, order_details, order.id)
        
        self._log_order_execution(order_details, account, action)
        
        return order.id
        
    except Exception as e:
        logger.error(f"Order failed for {signal.get('symbol', 'unknown')}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None

def _is_trade_allowed(self, symbol: str) -> bool:
    """Check if trade is allowed (market hours, etc.)"""
    if not self.is_market_open() and not symbol.endswith('-USD'):
        logger.warning(f"⏭️  Market is closed - skipping {symbol}")
        return False
    return True

def _prepare_order_details(self, signal: Dict, account, action: str) -> Optional[Dict]:
    """Prepare order details including quantity and side"""
    entry_price = signal.get('entry_price', 100)
    confidence = signal.get('confidence', 75)
    stop_price = signal.get('stop_price')
    target_price = signal.get('target_price')
    
    # Check for existing position (for SELL orders)
    if action == 'SELL':
        return self._prepare_sell_order_details(signal, account, entry_price)
    else:
        return self._prepare_buy_order_details(signal, account, entry_price, confidence, stop_price, target_price)

def _prepare_sell_order_details(self, signal: Dict, account, entry_price: float) -> Optional[Dict]:
    """Prepare details for SELL order (close position or new short)"""
    symbol = signal['symbol']
    positions = self.get_positions()
    existing_position = next((p for p in positions if p['symbol'] == symbol), None)
    
    if existing_position:
        # Close existing position
        qty = abs(int(existing_position['qty']))
        side = OrderSide.SELL if existing_position['side'] == 'LONG' else OrderSide.BUY
        return {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'entry_price': entry_price,
            'is_closing': True,
            'place_bracket': False
        }
    else:
        # New short position
        qty, side = self._calculate_position_size(signal, account, entry_price)
        return {
            'symbol': symbol,
            'qty': qty,
            'side': OrderSide.SELL,
            'entry_price': entry_price,
            'stop_price': signal.get('stop_price'),
            'target_price': signal.get('target_price'),
            'is_closing': False,
            'place_bracket': True
        }

def _prepare_buy_order_details(self, signal: Dict, account, entry_price: float, 
                               confidence: float, stop_price: Optional[float], 
                               target_price: Optional[float]) -> Optional[Dict]:
    """Prepare details for BUY order"""
    # Check if signal provides explicit qty
    signal_qty = signal.get('qty') or signal.get('filled_qty')
    if signal_qty and signal_qty > 0:
        return {
            'symbol': signal['symbol'],
            'qty': int(signal_qty),
            'side': OrderSide.BUY,
            'entry_price': entry_price,
            'is_closing': False,
            'place_bracket': False
        }
    
    # Calculate position size
    qty, _ = self._calculate_position_size(signal, account, entry_price)
    return {
        'symbol': signal['symbol'],
        'qty': qty,
        'side': OrderSide.BUY,
        'entry_price': entry_price,
        'stop_price': stop_price,
        'target_price': target_price,
        'is_closing': False,
        'place_bracket': True
    }

def _calculate_position_size(self, signal: Dict, account, entry_price: float) -> Tuple[int, OrderSide]:
    """Calculate position size based on confidence, volatility, and config"""
    base_position_size_pct = self.config.get('position_size_pct', 10)
    max_position_size_pct = self.config.get('max_position_size_pct', 15)
    confidence = signal.get('confidence', 75)
    
    # Apply volatility adjustment
    volatility = self.get_asset_volatility(signal['symbol'])
    avg_volatility = 0.02
    volatility_multiplier = min(avg_volatility / volatility if volatility > 0 else 1.0, 1.5)
    
    # Scale by confidence
    if confidence >= 75:
        confidence_multiplier = 1.0 + ((confidence - 75) / 25) * 0.5
        position_size_pct = min(base_position_size_pct * confidence_multiplier * volatility_multiplier, max_position_size_pct)
    else:
        position_size_pct = base_position_size_pct * 0.75 * volatility_multiplier
    
    buying_power = float(account.buying_power)
    position_value = buying_power * (position_size_pct / 100)
    qty = int(position_value / entry_price)
    
    side = OrderSide.BUY if signal['action'] == 'BUY' else OrderSide.SELL
    
    return qty, side

def _submit_main_order(self, order_details: Dict):
    """Submit the main order (market or limit)"""
    use_limit_orders = self.config.get('use_limit_orders', False)
    limit_offset_pct = self.config.get('limit_order_offset_pct', 0.001)
    
    if use_limit_orders and not order_details.get('is_closing'):
        limit_price = self._calculate_limit_price(
            order_details['entry_price'], 
            order_details['side'], 
            limit_offset_pct
        )
        order_request = LimitOrderRequest(
            symbol=order_details['symbol'],
            qty=order_details['qty'],
            side=order_details['side'],
            limit_price=limit_price,
            time_in_force=TimeInForce.DAY
        )
    else:
        order_request = MarketOrderRequest(
            symbol=order_details['symbol'],
            qty=order_details['qty'],
            side=order_details['side'],
            time_in_force=TimeInForce.DAY
        )
    
    return self.alpaca.submit_order(order_request)

def _calculate_limit_price(self, entry_price: float, side: OrderSide, offset_pct: float) -> float:
    """Calculate limit price with offset"""
    if side == OrderSide.BUY:
        return entry_price * (1 + offset_pct)
    else:
        return entry_price * (1 - offset_pct)

def _place_bracket_orders(self, symbol: str, order_details: Dict, main_order_id: str):
    """Place stop loss and take profit orders"""
    qty = order_details['qty']
    stop_price = order_details.get('stop_price')
    target_price = order_details.get('target_price')
    side = order_details['side']
    
    if not (stop_price and target_price):
        return
    
    try:
        # Place stop loss
        stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
        stop_order = StopLossRequest(
            symbol=symbol,
            qty=qty,
            stop_price=stop_price,
            time_in_force=TimeInForce.GTC
        )
        stop_order_result = self.alpaca.submit_order(stop_order)
        logger.info(f"🛡️  Stop loss order placed: {stop_order_result.id} @ ${stop_price:.2f}")
        
        # Place take profit
        profit_order = TakeProfitRequest(
            symbol=symbol,
            qty=qty,
            limit_price=target_price,
            time_in_force=TimeInForce.GTC
        )
        profit_order_result = self.alpaca.submit_order(profit_order)
        logger.info(f"🎯 Take profit order placed: {profit_order_result.id} @ ${target_price:.2f}")
        
        # Track bracket orders
        if main_order_id in self._order_tracker:
            self._order_tracker[main_order_id]['stop_order_id'] = stop_order_result.id
            self._order_tracker[main_order_id]['profit_order_id'] = profit_order_result.id
    except Exception as e:
        logger.warning(f"Could not place stop loss/take profit orders: {e}")

def _track_order(self, order, signal: Dict, order_details: Dict):
    """Track order in internal tracker"""
    self._order_tracker[order.id] = {
        'symbol': order_details['symbol'],
        'side': order_details['side'].value,
        'qty': order_details['qty'],
        'entry_price': order_details['entry_price'],
        'signal': signal,
        'timestamp': datetime.utcnow().isoformat()
    }

def _log_order_execution(self, order_details: Dict, account, action: str):
    """Log order execution details"""
    symbol = order_details['symbol']
    qty = order_details['qty']
    entry_price = order_details['entry_price']
    side = order_details['side']
    
    if order_details.get('is_closing'):
        logger.info(f"✅ {side.value} {qty} {symbol} @ ${entry_price:.2f} (closing position)")
    else:
        position_value = qty * entry_price
        position_size_pct = (position_value / float(account.buying_power)) * 100 if action == 'BUY' else 0
        order_type = "LIMIT" if self.config.get('use_limit_orders', False) else "MARKET"
        logger.info(f"✅ {order_type} {side.value} {qty} {symbol} @ ${entry_price:.2f} (${position_value:,.2f}, {position_size_pct:.1f}% of buying power)")
```

**Benefits:**
- Clear separation of order preparation, submission, and tracking
- Easier to test each component
- Better error handling
- More maintainable and readable

---

## Summary of Refactoring Benefits

1. **Single Responsibility Principle**: Each method now has one clear purpose
2. **Testability**: Smaller methods are easier to unit test
3. **Maintainability**: Changes are isolated to specific methods
4. **Readability**: Code is easier to understand and navigate
5. **Reusability**: Extracted methods can be reused
6. **Error Handling**: Better error isolation and handling

## Next Steps

1. Start with the longest functions first (`generate_signal_for_symbol`, `_init_data_sources`, `_execute_live`)
2. Create unit tests for each extracted method
3. Refactor incrementally, testing after each change
4. Consider using dependency injection for better testability
5. Add type hints where missing for better IDE support

