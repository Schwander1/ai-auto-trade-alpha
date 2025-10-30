#!/bin/bash
cd "$(dirname "$0")"
mkdir -p /tmp/clickhouse
clickhouse-server --config-file=config/config.xml --daemon --pid-file=clickhouse-server.pid
