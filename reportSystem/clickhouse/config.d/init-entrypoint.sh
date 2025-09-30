#!/bin/bash
set -e

echo "Starting ClickHouse server..."
/entrypoint.sh &

CLICKHOUSE_PID=$!

echo "Waiting for ClickHouse to start..."
# Ждем пока ClickHouse станет доступен
for i in {1..30}; do
    if clickhouse-client --user=admin --password=admin123 --query="SELECT 1" 2>/dev/null; then
        echo "ClickHouse is ready!"
        break
    fi
    echo "Waiting for ClickHouse... (attempt $i/30)"
    sleep 2
done

if ! clickhouse-client --user=admin --password=admin123 --query="SELECT 1" 2>/dev/null; then
    echo "ClickHouse failed to start within 60 seconds"
    exit 1
fi

echo "ClickHouse started successfully!"

echo "Running initialization scripts..."
for sql in /docker-entrypoint-initdb.d/*.sql; do
    if [ -f "$sql" ]; then
        echo "Executing: $sql"
        clickhouse-client --user=admin --password=admin123 --multiquery < "$sql"
    fi
done

echo "ClickHouse initialization completed!"

wait $CLICKHOUSE_PID