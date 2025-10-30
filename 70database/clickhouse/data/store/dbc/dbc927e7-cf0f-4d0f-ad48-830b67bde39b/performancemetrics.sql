ATTACH TABLE _ UUID '1c9bf353-8a19-4be3-a9b7-27b60f3d39e3'
(
    `timestamp` DateTime,
    `portfoliovalue` Float64,
    `dailypnl` Float64,
    `totalreturn` Float64,
    `sharperatio` Float64,
    `maxdrawdown` Float64,
    `winrate` Float64,
    `activepositions` UInt32,
    `risklevel` String DEFAULT 'CONSERVATIVE'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY timestamp
SETTINGS index_granularity = 8192
