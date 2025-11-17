# Centralized Log Aggregation Guide

Guide for setting up centralized log aggregation and search using ELK Stack (Elasticsearch, Logstash, Kibana) or Loki.

## Table of Contents

1. [Overview](#overview)
2. [ELK Stack Setup](#elk-stack-setup)
3. [Loki Setup](#loki-setup)
4. [Application Logging](#application-logging)
5. [Log Shipping](#log-shipping)
6. [Search and Analysis](#search-and-analysis)
7. [Best Practices](#best-practices)

---

## Overview

### Why Centralized Logging?

- **Unified View**: All logs in one place
- **Search**: Fast search across all services
- **Analysis**: Identify patterns and issues
- **Alerting**: Set up alerts on log patterns
- **Compliance**: Audit trail and retention

### Options

1. **ELK Stack** (Elasticsearch, Logstash, Kibana)
   - Full-featured, powerful search
   - Good for complex queries
   - Higher resource requirements

2. **Loki + Grafana**
   - Lightweight, cost-effective
   - Integrates with existing Grafana
   - Good for simple log aggregation

---

## ELK Stack Setup

### Docker Compose Setup

Create `infrastructure/logging/docker-compose.elk.yml`:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/config:/usr/share/logstash/config
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"
      - "9600:9600"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### Logstash Configuration

**`infrastructure/logging/logstash/config/logstash.yml`**:
```yaml
http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.hosts: [ "http://elasticsearch:9200" ]
```

**`infrastructure/logging/logstash/pipeline/logstash.conf`**:
```ruby
input {
  beats {
    port => 5044
  }

  # Direct TCP input for application logs
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  # Parse application logs
  if [service] == "argo" or [service] == "alpine-backend" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} - %{WORD:logger} - %{LOGLEVEL:level} - %{GREEDYDATA:message}" }
    }

    date {
      match => [ "timestamp", "yyyy-MM-dd HH:mm:ss,SSS" ]
    }
  }

  # Add environment tag
  if [environment] {
    mutate {
      add_tag => [ "%{environment}" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{service}-%{+YYYY.MM.dd}"
  }
}
```

### Filebeat Configuration

**`infrastructure/logging/filebeat/filebeat.yml`**:
```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/argo/*.log
      - /var/log/alpine-backend/*.log
    fields:
      service: argo
      environment: production
    fields_under_root: true

output.logstash:
  hosts: ["logstash:5044"]

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
```

---

## Loki Setup

### Docker Compose Setup

Create `infrastructure/logging/docker-compose.loki.yml`:

```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./loki/config:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/loki-config.yaml

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./promtail/config:/etc/promtail
      - /var/log:/var/log:ro
    command: -config.file=/etc/promtail/promtail-config.yaml

volumes:
  loki_data:
```

### Loki Configuration

**`infrastructure/logging/loki/config/loki-config.yaml`**:
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days
```

### Promtail Configuration

**`infrastructure/logging/promtail/config/promtail-config.yaml`**:
```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: argo
    static_configs:
      - targets:
          - localhost
        labels:
          job: argo
          service: argo
          __path__: /var/log/argo/*.log

  - job_name: alpine-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: alpine-backend
          service: alpine-backend
          __path__: /var/log/alpine-backend/*.log
```

### Grafana Data Source

Add Loki as data source in Grafana:

1. Go to Configuration → Data Sources
2. Add data source → Loki
3. URL: `http://loki:3100`
4. Save & Test

---

## Application Logging

### Structured Logging

**Python (Alpine Backend)**:
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': 'alpine-backend',
            'environment': os.getenv('ENVIRONMENT', 'development'),
        }

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Node.js (Alpine Frontend)**:
```javascript
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'alpine-frontend',
    environment: process.env.NODE_ENV,
  },
  transports: [
    new winston.transports.File({ filename: '/var/log/alpine-frontend/error.log', level: 'error' }),
    new winston.transports.File({ filename: '/var/log/alpine-frontend/combined.log' }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}
```

---

## Log Shipping

### Option 1: Filebeat (ELK)

```bash
# Install Filebeat
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.0-linux-x86_64.tar.gz
tar xzvf filebeat-8.11.0-linux-x86_64.tar.gz
cd filebeat-8.11.0-linux-x86_64

# Configure
cp filebeat.yml filebeat.yml.bak
# Edit filebeat.yml (see configuration above)

# Start
./filebeat -e
```

### Option 2: Promtail (Loki)

```bash
# Run Promtail via Docker
docker run -d \
  -v /var/log:/var/log:ro \
  -v ./promtail-config.yaml:/etc/promtail/promtail-config.yaml \
  grafana/promtail:2.9.0 \
  -config.file=/etc/promtail/promtail-config.yaml
```

### Option 3: Direct TCP/UDP

**Python**:
```python
import logging
import socket
import json

class TCPLogHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def emit(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'service': 'alpine-backend',
        }
        self.sock.send((json.dumps(log_data) + '\n').encode())

# Add handler
logger.addHandler(TCPLogHandler('logstash', 5000))
```

---

## Search and Analysis

### Kibana Queries (ELK)

**Find errors in last hour**:
```
level:ERROR AND @timestamp:[now-1h TO now]
```

**Find slow requests**:
```
message:"duration" AND duration:>1000
```

**Group by service**:
```
service:argo OR service:alpine-backend
```

### Loki Queries (Grafana)

**Find errors**:
```logql
{service="alpine-backend"} |= "ERROR"
```

**Count errors by level**:
```logql
sum(count_over_time({service="alpine-backend"} |= "ERROR" [5m])) by (level)
```

**Find slow requests**:
```logql
{service="alpine-backend"} | json | duration > 1000
```

---

## Best Practices

1. **Structured Logging**: Use JSON format for easy parsing
2. **Log Levels**: Use appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. **PII Redaction**: Don't log sensitive data (passwords, tokens, PII)
4. **Context**: Include request IDs, user IDs, service names
5. **Retention**: Set appropriate retention periods
6. **Indexing**: Index frequently queried fields
7. **Alerting**: Set up alerts for critical errors

---

## Resources

- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
