ATTACH TABLE _ UUID '46fb43ad-9332-4103-ba04-8a3be2c6bee5'
(
    `timestamp` DateTime,
    `symbol` String,
    `price` Float64,
    `volume` UInt64,
    `high` Float64,
    `low` Float64,
    `open` Float64,
    `close` Float64,
    `source` String DEFAULT 'alphavantage'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192
