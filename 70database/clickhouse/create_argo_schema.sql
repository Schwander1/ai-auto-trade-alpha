-- ARGO Capital ClickHouse Trading Database Schema

CREATE DATABASE IF NOT EXISTS argo_capital;

USE argo_capital;

-- Market Data Table (Optimized for time-series)
CREATE TABLE IF NOT EXISTS market_data (
    timestamp DateTime64(3, 'UTC'),
    symbol String,
    price Float64,
    volume UInt64,
    high Float64,
    low Float64,
    open Float64,
    close Float64,
    source String DEFAULT 'alpha_vantage'
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192;

-- Trading Signals Table
CREATE TABLE IF NOT EXISTS trading_signals (
    timestamp DateTime64(3, 'UTC'),
    symbol String,
    signal Enum8('BUY' = 1, 'SELL' = 2, 'HOLD' = 3),
    strength Float64,
    confidence Float64,
    price_target Float64,
    model_version String,
    created_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192;

-- Portfolio Positions Table
CREATE TABLE IF NOT EXISTS portfolio_positions (
    timestamp DateTime64(3, 'UTC'),
    symbol String,
    quantity Float64,
    avg_cost Float64,
    current_price Float64,
    market_value Float64,
    unrealized_pnl Float64,
    weight_pct Float64,
    sector String,
    created_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192;

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    timestamp DateTime64(3, 'UTC'),
    portfolio_value Float64,
    daily_pnl Float64,
    total_return Float64,
    sharpe_ratio Float64,
    max_drawdown Float64,
    win_rate Float64,
    active_positions UInt32,
    risk_level String,
    created_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY timestamp
SETTINGS index_granularity = 8192;

-- Risk Metrics Table
CREATE TABLE IF NOT EXISTS risk_metrics (
    timestamp DateTime64(3, 'UTC'),
    portfolio_var_95 Float64,
    portfolio_var_99 Float64,
    expected_shortfall Float64,
    portfolio_beta Float64,
    correlation_spy Float64,
    max_position_weight Float64,
    leverage_ratio Float64,
    created_at DateTime64(3, 'UTC') DEFAULT now64()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY timestamp
SETTINGS index_granularity = 8192;

-- Portfolio summary materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS portfolio_summary_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY timestamp
AS SELECT
    toStartOfHour(timestamp) as timestamp,
    sum(market_value) as total_portfolio_value,
    sum(unrealized_pnl) as total_unrealized_pnl,
    count() as position_count
FROM portfolio_positions
GROUP BY toStartOfHour(timestamp);

