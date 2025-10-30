ATTACH TABLE _ UUID '02acd391-7718-4834-9d30-f47212536ab0'
(
    `timestamp` DateTime,
    `symbol` String,
    `quantity` Float64,
    `avg_cost` Float64,
    `current_price` Float64,
    `market_value` Float64,
    `unrealized_pnl` Float64,
    `weight_pct` Float64,
    `sector` String
)
ENGINE = ReplacingMergeTree
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192
