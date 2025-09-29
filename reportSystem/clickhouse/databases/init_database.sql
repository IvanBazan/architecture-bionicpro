CREATE DATABASE IF NOT EXISTS report;

CREATE USER IF NOT EXISTS app_user IDENTIFIED WITH plaintext_password BY 'app_password';

GRANT ALL ON report.* TO app_user;

CREATE TABLE IF NOT EXISTS report.users
(
    user_id Int32,
    username String,
    email String,
    first_name String,
    last_name String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY intDiv(user_id, 1000)
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS report.telemetry
(
    id Int32,
    user_id Int32,
    timestamp DateTime DEFAULT now(),
    valueA Int32,
    valueB Int32,
    valueC Int32,
    valueD Decimal(3, 1)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp, id)
SETTINGS index_granularity = 8192;

ALTER TABLE report.users ADD INDEX IF NOT EXISTS username_idx username TYPE bloom_filter GRANULARITY 1;
ALTER TABLE report.telemetry ADD INDEX IF NOT EXISTS user_id_idx user_id TYPE minmax GRANULARITY 1;
ALTER TABLE report.telemetry ADD INDEX IF NOT EXISTS timestamp_idx timestamp TYPE minmax GRANULARITY 1;


SELECT 
    'Database and tables created successfully' as result,
    count() as tables_created
FROM system.tables 
WHERE database = 'report';