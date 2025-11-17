# Load Testing Guide

Comprehensive guide for load testing the Argo → Alpine platform using k6 and Locust.

## Table of Contents

1. [Overview](#overview)
2. [k6 Setup](#k6-setup)
3. [Locust Setup](#locust-setup)
4. [Test Scenarios](#test-scenarios)
5. [Running Tests](#running-tests)
6. [Performance Benchmarks](#performance-benchmarks)
7. [CI/CD Integration](#cicd-integration)

---

## Overview

### Why Load Testing?

- **Capacity Planning**: Understand system limits
- **Performance Validation**: Ensure SLAs are met
- **Bottleneck Identification**: Find performance issues
- **Regression Testing**: Detect performance regressions

### Tools

- **k6**: Modern load testing tool (JavaScript-based, cloud-native)
- **Locust**: Python-based load testing framework

---

## k6 Setup

### Installation

```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker pull grafana/k6
```

### Basic Test Script

Create `scripts/load-tests/k6/basic-test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 20 },    // Stay at 20 users
    { duration: '30s', target: 50 },   // Ramp up to 50 users
    { duration: '1m', target: 50 },    // Stay at 50 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],                  // Error rate < 1%
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';

export default function () {
  // Health check
  let res = http.get(`${BASE_URL}/health`);
  check(res, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  }) || errorRate.add(1);

  sleep(1);

  // API endpoint test
  res = http.get(`${BASE_URL}/api/v1/signals?limit=10`);
  check(res, {
    'signals endpoint status is 200': (r) => r.status === 200,
    'signals response time < 500ms': (r) => r.timings.duration < 500,
    'signals response has data': (r) => JSON.parse(r.body).length > 0,
  }) || errorRate.add(1);

  sleep(2);
}
```

### Running k6 Tests

```bash
# Run basic test
k6 run scripts/load-tests/k6/basic-test.js

# With environment variable
BASE_URL=http://localhost:8001 k6 run scripts/load-tests/k6/basic-test.js

# With custom VUs and duration
k6 run --vus 50 --duration 5m scripts/load-tests/k6/basic-test.js

# Output to InfluxDB (for Grafana)
k6 run --out influxdb=http://localhost:8086/k6 scripts/load-tests/k6/basic-test.js
```

---

## Locust Setup

### Installation

```bash
pip install locust
```

### Basic Test Script

Create `scripts/load-tests/locust/locustfile.py`:

```python
from locust import HttpUser, task, between
import random

class AlpineAPIUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a user starts"""
        # Login or setup
        pass

    @task(3)
    def health_check(self):
        """Health check endpoint (weight: 3)"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(5)
    def get_signals(self):
        """Get signals endpoint (weight: 5)"""
        limit = random.choice([10, 20, 50])
        with self.client.get(f"/api/v1/signals?limit={limit}", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    response.success()
                else:
                    response.failure("Empty response")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def get_signal_by_id(self):
        """Get specific signal (weight: 2)"""
        signal_id = random.randint(1, 1000)
        with self.client.get(f"/api/v1/signals/{signal_id}", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
```

### Running Locust Tests

```bash
# Start Locust web UI
locust -f scripts/load-tests/locust/locustfile.py --host=http://localhost:8001

# Headless mode
locust -f scripts/load-tests/locust/locustfile.py \
  --host=http://localhost:8001 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless

# With HTML report
locust -f scripts/load-tests/locust/locustfile.py \
  --host=http://localhost:8001 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless \
  --html reports/locust-report.html
```

---

## Test Scenarios

### Scenario 1: API Endpoints

**File**: `scripts/load-tests/k6/api-endpoints.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';

export default function () {
  // Test multiple endpoints
  const endpoints = [
    '/health',
    '/api/v1/signals',
    '/api/v1/signals/live/AAPL',
    '/api/v1/performance/stats',
  ];

  for (const endpoint of endpoints) {
    const res = http.get(`${BASE_URL}${endpoint}`);
    check(res, {
      [`${endpoint} status is 200`]: (r) => r.status === 200,
    });
    sleep(0.5);
  }
}
```

### Scenario 2: Rate Limiting

**File**: `scripts/load-tests/k6/rate-limit-test.js`

```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 200,  // High number of users
  duration: '2m',
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    'http_reqs{status:429}': ['rate>0'],  // Expect some 429s
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';

export default function () {
  const res = http.get(`${BASE_URL}/api/v1/signals`);

  check(res, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429,
    'rate limit headers present': (r) => r.headers['X-RateLimit-Limit'] !== undefined,
  });
}
```

### Scenario 3: Database Load

**File**: `scripts/load-tests/locust/database-load.py`

```python
from locust import HttpUser, task, between
import random

class DatabaseLoadUser(HttpUser):
    wait_time = between(0.5, 2)

    @task
    def complex_query(self):
        """Test complex database queries"""
        params = {
            'limit': random.choice([10, 20, 50, 100]),
            'offset': random.randint(0, 1000),
            'premium_only': random.choice([True, False]),
        }
        self.client.get("/api/v1/signals", params=params)
```

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Critical |
|--------|--------|----------|
| Health Check | < 100ms (p95) | < 200ms |
| API Endpoints | < 500ms (p95) | < 1000ms |
| Database Queries | < 200ms (p95) | < 500ms |
| Error Rate | < 0.1% | < 1% |
| Throughput | > 1000 req/s | > 500 req/s |

### Baseline Results

Run baseline tests before major changes:

```bash
# Save baseline results
k6 run --out json=baseline-results.json scripts/load-tests/k6/basic-test.js
```

Compare against baseline:

```bash
# Run new test
k6 run --out json=new-results.json scripts/load-tests/k6/basic-test.js

# Compare (requires k6-comparison tool)
k6-compare baseline-results.json new-results.json
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/load-test.yml`:

```yaml
name: Load Testing

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to test'
        required: true
        default: 'staging'

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load tests
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
        run: |
          k6 run --out json=results.json scripts/load-tests/k6/basic-test.js

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: results.json

      - name: Check thresholds
        run: |
          # Parse results and check if thresholds met
          python scripts/load-tests/check-thresholds.py results.json
```

### Performance Regression Detection

Create `scripts/load-tests/check-thresholds.py`:

```python
#!/usr/bin/env python3
"""Check if load test results meet thresholds"""
import json
import sys

THRESHOLDS = {
    'http_req_duration': {
        'p95': 500,  # 95th percentile < 500ms
        'p99': 1000,  # 99th percentile < 1000ms
    },
    'http_req_failed': {
        'rate': 0.01,  # Error rate < 1%
    },
}

def check_thresholds(results_file):
    with open(results_file) as f:
        data = json.load(f)

    metrics = data.get('metrics', {})
    failed = False

    for metric_name, thresholds in THRESHOLDS.items():
        if metric_name not in metrics:
            print(f"⚠️  Metric {metric_name} not found")
            continue

        metric = metrics[metric_name]

        for threshold_name, threshold_value in thresholds.items():
            if threshold_name == 'rate':
                value = metric.get('values', {}).get('rate', 0)
            elif threshold_name.startswith('p'):
                percentile = int(threshold_name[1:])
                value = metric.get('values', {}).get(f'p{percentile}', 0)
            else:
                continue

            if value > threshold_value:
                print(f"❌ {metric_name} {threshold_name}: {value} > {threshold_value}")
                failed = True
            else:
                print(f"✅ {metric_name} {threshold_name}: {value} <= {threshold_value}")

    return not failed

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: check-thresholds.py <results.json>")
        sys.exit(1)

    success = check_thresholds(sys.argv[1])
    sys.exit(0 if success else 1)
```

---

## Best Practices

1. **Start Small**: Begin with low load and gradually increase
2. **Test Realistic Scenarios**: Mimic real user behavior
3. **Monitor Resources**: Watch CPU, memory, database during tests
4. **Run Regularly**: Schedule weekly load tests
5. **Compare Baselines**: Track performance over time
6. **Test Edge Cases**: High load, spike tests, sustained load

---

## Resources

- [k6 Documentation](https://k6.io/docs/)
- [Locust Documentation](https://docs.locust.io/)
- [Performance Testing Best Practices](https://k6.io/docs/test-types/load-testing/)
