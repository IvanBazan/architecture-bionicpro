FROM clickhouse/clickhouse-server:23.3

COPY config.d/init-entrypoint.sh /etc/clickhouse-server/config.d/
RUN chmod +x /etc/clickhouse-server/config.d/init-entrypoint.sh

COPY databases/ /docker-entrypoint-initdb.d/

# Выставляем права для SQL скриптов
RUN chown -R clickhouse:clickhouse /docker-entrypoint-initdb.d/ \
    && chmod -R 644 /docker-entrypoint-initdb.d/ \
    && find /docker-entrypoint-initdb.d/ -name "*.sh" -exec chmod +x {} \;

# Можно добавить healthcheck для мониторинга
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["clickhouse-client", "--query", "SELECT 1"]