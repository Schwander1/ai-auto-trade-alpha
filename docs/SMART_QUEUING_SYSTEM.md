# Smart Queuing System

## Overview

The Smart Queuing System automatically queues signals that cannot execute immediately due to account constraints (e.g., insufficient buying power, missing positions) and executes them when conditions are met.

## How It Works

### 1. Signal Rejection Detection

When a signal is distributed to an executor and rejected, the system checks the rejection reason:

```python
# Example rejection reasons that trigger queuing:
- "Insufficient buying power"
- "No position found"
- "Insufficient funds"
```

### 2. Automatic Queuing

If the rejection is due to account constraints, the signal is automatically queued:

```python
# Signal is queued with conditions
conditions = [
    {
        'type': 'needs_buying_power',
        'value': 1000.0  # Required buying power
    },
    {
        'type': 'needs_position',
        'symbol': 'MSFT'  # Required position
    }
]
```

### 3. Condition Monitoring

The queue monitor checks conditions every 30 seconds:

```python
# For each queued signal:
1. Check account state
2. Verify all conditions are met
3. If met, mark signal as "ready"
4. If not met, keep as "pending"
```

### 4. Automatic Execution

When conditions are met:
- Signal status changes to "ready"
- Signal can be executed automatically
- Execution is logged

## Queue Statuses

- **pending**: Waiting for conditions to be met
- **ready**: Conditions met, ready to execute
- **executing**: Currently being executed
- **executed**: Successfully executed
- **expired**: Expired (default: 24 hours)
- **cancelled**: Manually cancelled

## Priority System

Signals are prioritized by:
- Confidence level (higher = higher priority)
- Time queued (newer = higher priority)

Priority = Confidence × Time Factor

## Configuration

### Queue Expiration

Default: 24 hours

Signals expire after 24 hours if not executed. This prevents stale signals from executing.

### Check Interval

- Queue monitoring: 30 seconds
- Account state monitoring: 60 seconds

## Database Schema

```sql
CREATE TABLE signal_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    entry_price REAL NOT NULL,
    target_price REAL NOT NULL,
    stop_price REAL NOT NULL,
    confidence REAL NOT NULL,
    timestamp TEXT NOT NULL,
    conditions TEXT NOT NULL,  -- JSON array
    priority REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    queued_at TEXT NOT NULL,
    expires_at TEXT,
    executor_id TEXT,
    retry_count INTEGER DEFAULT 0,
    last_checked TEXT,
    executed_at TEXT,
    execution_error TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## API Usage

### Queue a Signal

```python
from argo.core.signal_queue import SignalQueue, ExecutionCondition

queue = SignalQueue()

conditions = [
    {
        'type': ExecutionCondition.NEEDS_BUYING_POWER.value,
        'value': 1000.0
    }
]

queue.queue_signal(signal, conditions, executor_id='argo')
```

### Get Queue Stats

```python
stats = queue.get_queue_stats()
# Returns: {'pending': 12, 'ready': 8, 'executed': 21, ...}
```

### Get Ready Signals

```python
ready_signals = queue.get_ready_signals(limit=10)
# Returns list of QueuedSignal objects
```

## Integration

The queue system is automatically integrated with:
- Signal distributor (queues rejected signals)
- Account state monitor (triggers queue processing)
- Execution dashboard (displays queue status)

## Benefits

1. **No Signals Lost**: All rejected signals are queued
2. **Automatic Execution**: Executes when conditions are met
3. **Priority-Based**: Higher confidence signals execute first
4. **Condition Tracking**: Knows exactly what's needed
5. **Automatic Expiration**: Prevents stale signals

## Monitoring

Monitor queue status via:
- Execution dashboard (`/execution`)
- API endpoint (`/api/v1/execution/queue`)
- Database queries

## Troubleshooting

### Signals not queuing
- Check rejection reasons match expected patterns
- Verify queue system is initialized
- Check logs for errors

### Signals not executing
- Verify account states are being monitored
- Check conditions are correct
- Verify signals haven't expired

### Queue growing too large
- Check account funding
- Review rejection reasons
- Consider adjusting expiration time
