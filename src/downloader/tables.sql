CREATE TABLE compredict.stock
(
    `stock_name` LowCardinality(String),
    `interval` LowCardinality(String),
    `ts` DateTime,
    `open` Float64,
    `high` Float64,
    `low` Float64,
    `close` Float64,
    `adj_close` Float64,
    `volume` Float64
)
ENGINE = MergeTree
PARTITION BY (stock_name, interval)
ORDER BY ts
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS compredict.forecast
(
  `stock_name` LowCardinality(String),
  `interval` LowCardinality(String),
  `forecast_date` DateTime('UTC'),
  `forecast_value` Float64,
  `run_date` DateTime('UTC'),
  `model_name` LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY (stock_name, interval)
ORDER BY forecast_date
SETTINGS index_granularity = 8192
