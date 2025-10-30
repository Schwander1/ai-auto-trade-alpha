ATTACH TABLE _ UUID '4a7a11cb-eaef-4231-aa75-dec715753aa4'
(
    `timestamp` DateTime,
    `symbol` String,
    `price` Float64,
    `volume` UInt64,
    `high` Float64,
    `low` Float64,
    `open` Float64,
    `close` Float64,
    `source` String
)
ENGINE = MergeTree
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192
