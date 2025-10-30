ATTACH TABLE _ UUID 'b39cff4b-50d8-45d1-813d-b82248a2b1ab'
(
    `timestamp` DateTime,
    `portfolio_value` Float64,
    `daily_pnl` Float64,
    `total_return` Float64,
    `sharpe_ratio` Float64,
    `max_drawdown` Float64,
    `win_rate` Float64,
    `active_positions` UInt32,
    `risk_level` String
)
ENGINE = MergeTree
ORDER BY timestamp
SETTINGS index_granularity = 8192
