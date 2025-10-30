ATTACH TABLE _ UUID '2f93785e-4767-4fdd-9aac-4c404b3b5098'
(
    `timestamp` DateTime,
    `symbol` String,
    `quantity` Float64,
    `avgcost` Float64,
    `currentprice` Float64,
    `marketvalue` Float64,
    `unrealizedpnl` Float64,
    `weightpct` Float64,
    `sector` String
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192
