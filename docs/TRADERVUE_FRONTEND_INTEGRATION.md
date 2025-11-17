# Tradervue Frontend Integration Guide

**Date:** 2025-01-XX  
**Status:** Ready for Integration

---

## Overview

This guide shows how to integrate Tradervue widgets and metrics into your Alpine Analytics frontend.

---

## Components Created

### 1. TradervueWidget Component

Location: `alpine-frontend/components/tradervue/TradervueWidget.tsx`

**Features:**
- Embeds Tradervue performance widgets
- Supports multiple widget types (equity, trades, performance)
- Automatic error handling
- Loading states

**Usage:**

```tsx
import TradervueWidget from '@/components/tradervue/TradervueWidget'

// Equity curve widget
<TradervueWidget 
  widgetType="equity" 
  width={800} 
  height={400} 
/>

// Trades widget
<TradervueWidget 
  widgetType="trades" 
  width={600} 
  height={500} 
/>

// Performance widget
<TradervueWidget 
  widgetType="performance" 
  width={600} 
  height={400} 
/>
```

### 2. TradervueMetrics Component

Location: `alpine-frontend/components/tradervue/TradervueMetrics.tsx`

**Features:**
- Displays performance metrics from Tradervue
- Responsive grid layout
- Trend indicators
- Configurable date range

**Usage:**

```tsx
import TradervueMetrics from '@/components/tradervue/TradervueMetrics'

// Display last 30 days
<TradervueMetrics days={30} />

// Display last 90 days
<TradervueMetrics days={90} />
```

### 3. TradervueProfileLink Component

Location: `alpine-frontend/components/tradervue/TradervueWidget.tsx`

**Features:**
- Link to public Tradervue profile
- Automatic URL fetching
- External link indicator

**Usage:**

```tsx
import { TradervueProfileLink } from '@/components/tradervue/TradervueWidget'

<TradervueProfileLink />
```

### 4. TradervueStatusBadge Component

Location: `alpine-frontend/components/tradervue/TradervueWidget.tsx`

**Features:**
- Shows "Verified by Tradervue" badge
- Only displays if integration is enabled
- Green checkmark indicator

**Usage:**

```tsx
import { TradervueStatusBadge } from '@/components/tradervue/TradervueWidget'

<TradervueStatusBadge />
```

---

## Integration Examples

### Example 1: Dashboard Integration

Add to `alpine-frontend/app/dashboard/page.tsx`:

```tsx
import TradervueWidget from '@/components/tradervue/TradervueWidget'
import TradervueMetrics from '@/components/tradervue/TradervueMetrics'
import { TradervueProfileLink, TradervueStatusBadge } from '@/components/tradervue/TradervueWidget'

export default function DashboardPage() {
  return (
    <div>
      {/* Status Badge */}
      <div className="mb-4">
        <TradervueStatusBadge />
      </div>

      {/* Performance Metrics */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Verified Performance</h2>
        <TradervueMetrics days={30} />
        <div className="mt-4">
          <TradervueProfileLink />
        </div>
      </section>

      {/* Equity Curve Widget */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Equity Curve</h2>
        <TradervueWidget 
          widgetType="equity" 
          width={800} 
          height={400} 
        />
      </section>

      {/* Trades Widget */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Recent Trades</h2>
        <TradervueWidget 
          widgetType="trades" 
          width={800} 
          height={500} 
        />
      </section>
    </div>
  )
}
```

### Example 2: Performance Page

Create `alpine-frontend/app/performance/page.tsx`:

```tsx
'use client'

import TradervueWidget from '@/components/tradervue/TradervueWidget'
import TradervueMetrics from '@/components/tradervue/TradervueMetrics'
import { TradervueProfileLink } from '@/components/tradervue/TradervueWidget'

export default function PerformancePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Performance Metrics</h1>
        <p className="text-gray-400">
          Verified trading performance tracked by Tradervue
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="mb-8">
        <TradervueMetrics days={30} />
      </div>

      {/* Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-bold mb-4">Equity Curve</h2>
          <TradervueWidget 
            widgetType="equity" 
            width={600} 
            height={400} 
          />
        </div>
        <div>
          <h2 className="text-xl font-bold mb-4">Performance</h2>
          <TradervueWidget 
            widgetType="performance" 
            width={600} 
            height={400} 
          />
        </div>
      </div>

      {/* Profile Link */}
      <div className="text-center">
        <TradervueProfileLink />
      </div>
    </div>
  )
}
```

### Example 3: API Route (Alternative)

If you prefer to fetch data server-side, create an API route:

`alpine-frontend/app/api/tradervue/widget/route.ts`:

```typescript
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const widgetType = searchParams.get('widget_type') || 'equity'
  const width = searchParams.get('width') || '600'
  const height = searchParams.get('height') || '400'

  try {
    // Forward request to Argo API
    const argoUrl = process.env.ARGO_API_URL || 'http://localhost:8000'
    const response = await fetch(
      `${argoUrl}/api/v1/tradervue/widget-url?widget_type=${widgetType}&width=${width}&height=${height}`
    )

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch widget URL' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## Styling

The components use Tailwind CSS classes that match your Alpine theme:

- `alpine-black-secondary` - Background color
- `alpine-blue` - Primary accent color
- `alpine-blue-light` - Hover state
- `alpine-black-tertiary` - Border color

Customize as needed to match your design system.

---

## Error Handling

All components include error handling:

- **Loading States:** Shows spinner while fetching
- **Error States:** Displays error message if fetch fails
- **Graceful Degradation:** Hides component if not configured

---

## API Endpoints Used

The components use these API endpoints:

1. `GET /api/v1/tradervue/widget-url` - Get widget URL
2. `GET /api/v1/tradervue/profile-url` - Get profile URL
3. `GET /api/v1/tradervue/metrics` - Get performance metrics
4. `GET /api/v1/tradervue/status` - Get integration status

---

## Next Steps

1. **Import Components:** Add components to your pages
2. **Test Integration:** Verify widgets load correctly
3. **Customize Styling:** Match your design system
4. **Add to Navigation:** Link to performance page
5. **Monitor Performance:** Check widget load times

---

**Frontend Integration Ready!** ✅

