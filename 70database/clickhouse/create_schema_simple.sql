CREATE DATABASE IF NOT EXISTS argo_capital;
USE argo_capital;

CREATE TABLE IF NOT EXISTS market_data
( timestamp DateTime, symbol String, price Float64, volume UInt64,
  high Float64, low Float64, open Float64, close Float64, source String)
ENGINE=MergeTree() ORDER BY (symbol,timestamp);

CREATE TABLE IF NOT EXISTS portfolio_positions
( timestamp DateTime, symbol String, quantity Float64, avg_cost Float64,
  current_price Float64, market_value Float64, unrealized_pnl Float64,
  weight_pct Float64, sector String)
ENGINE=ReplacingMergeTree() ORDER BY (symbol,timestamp);

CREATE TABLE IF NOT EXISTS trading_signals
( timestamp DateTime, symbol String, signal String, strength Float64,
  confidence Float64, price_target Float64, model_version String)
ENGINE=MergeTree() ORDER BY (symbol,timestamp);

CREATE TABLE IF NOT EXISTS performance_metrics
( timestamp DateTime, portfolio_value Float64, daily_pnl Float64,
  total_return Float64, sharpe_ratio Float64, max_drawdown Float64,
  win_rate Float64, active_positions UInt32, risk_level String)
ENGINE=MergeTree() ORDER BY timestamp;
