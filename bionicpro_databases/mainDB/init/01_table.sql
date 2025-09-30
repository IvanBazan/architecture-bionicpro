CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valueA INTEGER,
    valueB INTEGER,
    valueC INTEGER,
    valueD DECIMAL(3,1)
);

CREATE INDEX IF NOT EXISTS idx_telemetry_user_id ON telemetry(user_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_user_timestamp ON telemetry(user_id, timestamp);
