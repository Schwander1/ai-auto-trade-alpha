ATTACH TABLE _ UUID 'c12d2ca5-7caf-42bc-b663-c23050e5898d'
(
    `timestamp` DateTime,
    `symbol` String,
    `signal` String,
    `strength` Float64,
    `confidence` Float64,
    `pricetarget` Float64,
    `modelversion` String DEFAULT 'v1.0'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192
