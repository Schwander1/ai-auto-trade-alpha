ATTACH TABLE _ UUID 'ae864dce-9197-485b-8f95-174283feb892'
(
    `timestamp` DateTime,
    `symbol` String,
    `signal` String,
    `strength` Float64,
    `confidence` Float64,
    `price_target` Float64,
    `model_version` String
)
ENGINE = MergeTree
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192
