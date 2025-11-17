# Frontend Rules (Alpine)

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** Alpine Frontend (Next.js)

---

## Overview

Frontend-specific rules for Alpine Analytics, focusing on Next.js, TypeScript, and React best practices.

---

## Performance Requirements

### Critical Non-Negotiables

#### Page Load
- **Initial page load:** <2 seconds (First Contentful Paint)
- **Target:** <1.5 seconds

#### API Response
- **API response:** <500ms (P95)
- **Target:** <300ms

#### WebSocket Latency
- **WebSocket latency:** <100ms (signal → browser)
- **Target:** <50ms

#### Core Web Vitals
- **LCP:** <2.5s (Largest Contentful Paint)
- **FID:** <100ms (First Input Delay)
- **CLS:** <0.1 (Cumulative Layout Shift)

#### Mobile Performance
- **Lighthouse score:** 90+ (mobile)
- **Target:** 95+

---

## Code Style

### File Naming
- **Format:** `kebab-case.tsx` or `kebab-case.ts`
- **Examples:**
  - `signal-card.tsx`
  - `dashboard-layout.tsx`
  - `use-websocket.ts`

### Component Naming
- **Format:** `PascalCase`
- **Examples:**
  ```typescript
  export default function SignalCard() {}
  export function DashboardLayout() {}
  ```

### Function Naming
- **Format:** `camelCase`
- **Examples:**
  ```typescript
  function calculateConfidence() {}
  const fetchSignalData = async () => {}
  ```

### Variable Naming
- **Format:** `camelCase`
- **Boolean prefix:** `is/has/should`
- **Examples:**
  ```typescript
  const isAuthenticated = true
  const hasSubscription = false
  const shouldShowModal = true
  ```

---

## Component Structure

### Component Template

```typescript
'use client' // Only if client component needed

import { useState, useEffect } from 'react'
import { Signal } from '@/types/signal'

interface SignalCardProps {
  signal: Signal
  onVerify?: (hash: string) => void
  className?: string
}

/**
 * SignalCard displays a trading signal with real-time updates and verification.
 * 
 * @param signal - Signal data from Argo backend
 * @param onVerify - Optional callback when user verifies signal hash
 * @param className - Additional Tailwind classes
 */
export default function SignalCard({ 
  signal, 
  onVerify,
  className = ''
}: SignalCardProps) {
  // 1. STATE DECLARATIONS
  const [isVerified, setIsVerified] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  // 2. EFFECTS
  useEffect(() => {
    // Auto-verify on mount
    verifySignal()
  }, [signal.id])
  
  // 3. EVENT HANDLERS
  const handleVerifyClick = async () => {
    setIsLoading(true)
    try {
      const result = await verifySignalHash(signal.hash, signal)
      setIsVerified(result)
      onVerify?.(signal.hash)
    } catch (error) {
      console.error('Verification failed:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  // 4. HELPER FUNCTIONS
  const formatConfidence = (value: number): string => {
    return `${value.toFixed(1)}%`
  }
  
  // 5. EARLY RETURNS (if needed)
  if (!signal) return null
  
  // 6. RENDER
  return (
    <div className={`rounded-lg border bg-white p-4 shadow-sm ${className}`}>
      {/* Component JSX */}
    </div>
  )
}
```

---

## Server vs Client Components

### Server Components (Default)
- **Use For:** Static content, data fetching, SEO-critical pages
- **No 'use client' directive**
- **Example:**
  ```typescript
  // app/dashboard/page.tsx
  import { getSignals } from '@/lib/api'
  
  export default async function DashboardPage() {
    const signals = await getSignals() // Fetch on server
    return <SignalList signals={signals} />
  }
  ```

### Client Components
- **Use For:** Interactivity, state, effects, browser APIs
- **Add 'use client' directive**
- **Example:**
  ```typescript
  // components/signal-list.tsx
  'use client'
  
  import { useState } from 'react'
  
  export default function SignalList({ signals }) {
    const [filter, setFilter] = useState('all')
    // Client-side filtering, interactions
    return <div>...</div>
  }
  ```

---

## TypeScript Rules

### Type Safety
- **Rule:** Zero TypeScript errors (strict mode)
- **Rule:** No `any` types
- **Action:** Use proper typing for all values

### Type Definitions
- **Location:** `types/` directory
- **Format:** `PascalCase` for types/interfaces
- **Example:**
  ```typescript
  interface SignalData {
    id: string
    symbol: string
    type: 'BUY' | 'SELL' | 'NEUTRAL'
    entry_price: number
    confidence: number
    timestamp: string
    hash: string
  }
  ```

---

## Performance Optimization

### Image Optimization
- **Rule:** ALWAYS use Next.js Image component
- **Example:**
  ```typescript
  import Image from 'next/image'
  
  <Image
    src="/logo.png"
    alt="Alpine Analytics Logo"
    width={200}
    height={50}
    priority // For above-the-fold images
  />
  ```

### Code Splitting
- **Rule:** Lazy load non-critical components
- **Example:**
  ```typescript
  import dynamic from 'next/dynamic'
  
  const HeavyChart = dynamic(() => import('@/components/heavy-chart'), {
    loading: () => <div>Loading chart...</div>,
    ssr: false // Disable server-side rendering if needed
  })
  ```

### Data Fetching
- **Server Components:** Use for initial data
- **Client Components:** Use for real-time updates
- **Example:**
  ```typescript
  // Server component
  export default async function DashboardPage() {
    const signals = await fetch('https://api.alpine.com/signals', {
      next: { revalidate: 60 } // Revalidate every 60 seconds
    }).then(res => res.json())
    return <SignalList signals={signals} />
  }
  
  // Client component for real-time
  'use client'
  export function useSignals() {
    const [signals, setSignals] = useState<Signal[]>([])
    useEffect(() => {
      const ws = new WebSocket('wss://api.alpine.com/ws')
      ws.onmessage = (event) => {
        const newSignal = JSON.parse(event.data)
        setSignals(prev => [newSignal, ...prev])
      }
      return () => ws.close()
    }, [])
    return signals
  }
  ```

---

## Tailwind CSS

### Responsive Design (Mobile-First)
```typescript
<div className="
  p-4           // Base (mobile): 16px padding
  sm:p-6        // Small (640px+): 24px padding
  md:p-8        // Medium (768px+): 32px padding
  lg:p-12       // Large (1024px+): 48px padding
">
  Content
</div>
```

### Component Variants
```typescript
import { cn } from '@/lib/utils'

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Button({ variant = 'primary', size = 'md', className }: ButtonProps) {
  return (
    <button className={cn(
      'rounded-md font-medium transition-colors',
      {
        'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
        'bg-gray-200 text-gray-900 hover:bg-gray-300': variant === 'secondary',
      },
      {
        'px-3 py-1.5 text-sm': size === 'sm',
        'px-4 py-2 text-base': size === 'md',
      },
      className
    )}>
      {children}
    </button>
  )
}
```

---

## Error Handling

### Error Boundaries
```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <button onClick={reset} className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white">
        Try again
      </button>
    </div>
  )
}
```

### Loading States
```typescript
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-12 rounded bg-gray-200" />
      <div className="h-64 rounded bg-gray-200" />
    </div>
  )
}
```

---

## Accessibility (WCAG 2.1 AA)

### ARIA Labels
```typescript
<button
  onClick={handleClick}
  aria-label="Verify trading signal"
  className="..."
>
  Verify Signal
</button>
```

### Semantic HTML
```typescript
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
  </ul>
</nav>
```

### Form Labels
```typescript
<label htmlFor="email" className="block text-sm font-medium">
  Email
</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-describedby="email-help"
/>
<p id="email-help" className="text-sm text-gray-600">
  We'll never share your email
</p>
```

---

## Testing Requirements

### Coverage
- **Minimum:** 80%+ test coverage
- **Target:** 90%+

### Tools
- **Unit Tests:** Jest + React Testing Library
- **E2E Tests:** Playwright

### Test Structure
```typescript
// __tests__/signal-card.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import SignalCard from '@/components/signal-card'

describe('SignalCard', () => {
  const mockSignal = {
    id: '123',
    symbol: 'AAPL',
    type: 'BUY',
    entry_price: 150.25,
    confidence: 95.3,
    hash: 'abc123...'
  }
  
  it('renders signal data correctly', () => {
    render(<SignalCard signal={mockSignal} />)
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('BUY')).toBeInTheDocument()
  })
})
```

---

## Pre-Deployment Checklist

- [ ] Lighthouse score >90 (mobile)
- [ ] <2s page load (tested on 3G)
- [ ] All TypeScript errors resolved
- [ ] 80%+ test coverage
- [ ] Accessibility audit passed
- [ ] Error boundaries implemented
- [ ] Loading states for all async operations
- [ ] Mobile responsive (tested on actual devices)
- [ ] WebSocket reconnection working
- [x] SHA-256 verification functional (client-side Web Crypto API)

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [03_TESTING.md](03_TESTING.md) - Testing requirements
- [08_DOCUMENTATION.md](08_DOCUMENTATION.md) - Documentation standards
- [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Monitoring and observability

