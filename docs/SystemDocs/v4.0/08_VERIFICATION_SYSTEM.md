# SHA-256 Verification System Guide

**Date:** January 15, 2025  
**Version:** 4.0  
**Status:** ✅ Complete

---

## Executive Summary

The SHA-256 Verification System provides cryptographic verification of trading signals to ensure data integrity and prevent tampering. The system includes both backend and frontend verification capabilities.

---

## Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Signal Generation (Backend)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Generate Signal                                  │   │
│  │  - Collect signal data                            │   │
│  │  - Calculate SHA-256 hash                         │   │
│  │  - Store hash with signal                         │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Signal Storage                                   │   │
│  │  - Signal data + SHA-256 hash                     │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Signal Delivery (API)                            │   │
│  │  - Send signal + hash to frontend                 │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Frontend Verification                            │   │
│  │  - Receive signal + hash                          │   │
│  │  - Recalculate hash from signal data              │   │
│  │  - Compare with stored hash                       │   │
│  │  - Display verification status                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Hash Calculation

### Hash Fields

The hash is calculated from the following fields (in sorted order):

```typescript
{
  signal_id: string,
  symbol: string,
  action: string,        // "BUY" or "SELL"
  entry_price: number,
  target_price: number | null,
  stop_price: number | null,
  confidence: number,
  strategy: string | null,
  timestamp: string
}
```

### Calculation Process

1. **Create Hash Object**
   ```typescript
   const hashFields = {
     signal_id: signal.signal_id || signal.id,
     symbol: signal.symbol,
     action: signal.action,
     entry_price: signal.entry_price,
     target_price: signal.target_price || signal.take_profit || null,
     stop_price: signal.stop_price || signal.stop_loss || null,
     confidence: signal.confidence,
     strategy: signal.strategy || null,
     timestamp: signal.timestamp,
   }
   ```

2. **Sort Keys**
   ```typescript
   const sortedKeys = Object.keys(hashFields).sort()
   const sortedFields: Record<string, any> = {}
   sortedKeys.forEach(key => {
     sortedFields[key] = hashFields[key as keyof typeof hashFields]
   })
   ```

3. **Convert to JSON**
   ```typescript
   const hashString = JSON.stringify(sortedFields)
   ```

4. **Calculate SHA-256**
   ```typescript
   const encoder = new TextEncoder()
   const data = encoder.encode(hashString)
   const hashBuffer = await crypto.subtle.digest('SHA-256', data)
   const hashArray = Array.from(new Uint8Array(hashBuffer))
   const calculatedHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
   ```

5. **Compare**
   ```typescript
   const isValid = calculatedHash.toLowerCase() === signal.hash.toLowerCase()
   ```

---

## Backend Implementation

### Python (Argo Backend)

```python
import hashlib
import json

def generate_signal_hash(signal_data: Dict) -> str:
    """Generate SHA-256 hash of signal data"""
    hash_fields = {
        'signal_id': signal_data.get('signal_id'),
        'symbol': signal_data.get('symbol'),
        'action': signal_data.get('action'),
        'entry_price': signal_data.get('entry_price'),
        'target_price': signal_data.get('target_price'),
        'stop_price': signal_data.get('stop_price'),
        'confidence': signal_data.get('confidence'),
        'strategy': signal_data.get('strategy'),
        'timestamp': signal_data.get('timestamp')
    }
    
    hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
```

### Verification

```python
def verify_signal_hash(signal: Dict) -> bool:
    """Verify signal hash matches data"""
    stored_hash = signal.get('verification_hash') or signal.get('sha256')
    if not stored_hash:
        return False
    
    calculated_hash = generate_signal_hash(signal)
    return calculated_hash == stored_hash
```

---

## Frontend Implementation

### TypeScript/React

```typescript
const verifySignalHash = async (): Promise<SignalVerification> => {
  try {
    // Check hash format
    if (!signal.hash || signal.hash.length !== 64 || !/^[a-f0-9]+$/i.test(signal.hash)) {
      return {
        isValid: false,
        verifiedAt: new Date().toISOString(),
        error: 'Invalid hash format',
      }
    }

    // Build hash fields
    const hashFields = {
      signal_id: signal.signal_id || signal.id,
      symbol: signal.symbol,
      action: signal.action,
      entry_price: signal.entry_price,
      target_price: signal.target_price || signal.take_profit || null,
      stop_price: signal.stop_price || signal.stop_loss || null,
      confidence: signal.confidence,
      strategy: signal.strategy || null,
      timestamp: signal.timestamp,
    }

    // Sort and stringify
    const sortedKeys = Object.keys(hashFields).sort()
    const sortedFields: Record<string, any> = {}
    sortedKeys.forEach(key => {
      sortedFields[key] = hashFields[key as keyof typeof hashFields]
    })
    const hashString = JSON.stringify(sortedFields)

    // Calculate SHA-256
    const encoder = new TextEncoder()
    const data = encoder.encode(hashString)
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const calculatedHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')

    // Compare
    const isValid = calculatedHash.toLowerCase() === signal.hash.toLowerCase()

    return {
      isValid,
      verifiedAt: new Date().toISOString(),
      error: isValid ? undefined : 'Hash verification failed - signal data may have been tampered with',
    }
  } catch (error) {
    return {
      isValid: false,
      verifiedAt: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Verification error',
    }
  }
}
```

---

## Usage

### Signal Card Component

```tsx
import { useState } from 'react'
import { Shield } from 'lucide-react'

export default function SignalCard({ signal }) {
  const [isVerified, setIsVerified] = useState(false)
  const [verificationError, setVerificationError] = useState<string | undefined>()

  const handleVerify = async () => {
    const result = await verifySignalHash()
    setIsVerified(result.isValid)
    if (!result.isValid) {
      setVerificationError(result.error)
    }
  }

  return (
    <div>
      {isVerified ? (
        <div className="flex items-center gap-2 text-alpine-neon-cyan">
          <Shield className="w-4 h-4" />
          <span className="text-sm font-semibold">SHA-256 Verified</span>
        </div>
      ) : (
        <button onClick={handleVerify}>Verify Signal</button>
      )}
      {verificationError && (
        <div className="text-alpine-semantic-error">{verificationError}</div>
      )}
    </div>
  )
}
```

---

## Integrity Monitoring

### Automated Verification

The integrity monitor automatically verifies signals:

```python
# argo/argo/compliance/integrity_monitor.py
def run_integrity_check(self, sample_size: Optional[int] = None) -> Dict:
    """Run integrity check on signals"""
    signals = self._query_signals(sample_size)
    
    failed_count = 0
    for signal in signals:
        is_valid = self._verify_signal_hash(signal)
        if not is_valid:
            failed_count += 1
            # Trigger alert
            self._trigger_alert(results)
    
    return {
        'success': failed_count == 0,
        'checked': len(signals),
        'failed': failed_count
    }
```

---

## Security Considerations

1. **Hash Format Validation**
   - Verify hash is 64 characters
   - Verify hash is hexadecimal
   - Reject invalid formats

2. **Case Insensitive Comparison**
   - Use `.toLowerCase()` for comparison
   - Handle both uppercase and lowercase hashes

3. **Error Handling**
   - Catch and handle verification errors
   - Provide clear error messages
   - Log verification failures

4. **Performance**
   - Verification is asynchronous
   - Uses Web Crypto API (browser native)
   - Minimal performance impact

---

## Best Practices

1. **Always Verify**
   - Verify signals before displaying
   - Show verification status to users
   - Log verification failures

2. **Handle Failures**
   - Display clear error messages
   - Alert on verification failures
   - Investigate failed verifications

3. **Monitor Integrity**
   - Run automated integrity checks
   - Track verification success rates
   - Alert on integrity failures

---

## Troubleshooting

### Verification Fails

1. Check hash format (64 hex characters)
2. Verify field names match exactly
3. Check field values are correct
4. Verify JSON serialization matches

### Performance Issues

1. Verification is async - use await
2. Cache verification results
3. Batch verify multiple signals

---

**Related Documentation:**
- `06_ALERTING_SYSTEM.md` - Alerting on verification failures
- `04_SYSTEM_MONITORING_COMPLETE_GUIDE.md` - Integrity monitoring

