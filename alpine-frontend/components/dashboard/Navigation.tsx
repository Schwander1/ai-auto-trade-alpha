'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useMemo, useCallback } from 'react'
import { 
  LayoutDashboard, Signal, BarChart3, User, 
  CreditCard, Settings, LogOut
} from 'lucide-react'
import { signOut } from 'next-auth/react'
import UserMenu from './UserMenu'
import TradingEnvironmentBadge from './TradingEnvironmentBadge'

/**
 * Navigation component for dashboard pages
 * Optimized with memoization for better performance
 */
export default function Navigation() {
  const pathname = usePathname()

  const navItems = useMemo(() => [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/signals', label: 'Signals', icon: Signal },
    { href: '/backtest', label: 'Backtest', icon: BarChart3 },
    { href: '/account', label: 'Account', icon: User },
    { href: '/pricing', label: 'Pricing', icon: CreditCard },
  ], [])

  const isActive = useCallback((href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname?.startsWith(href)
  }, [pathname])

  return (
    <nav className="bg-alpine-black-secondary border-b-border-alpine-black-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="text-xl font-bold text-alpine-text-primary ">
              Alpine Analytics
            </Link>
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                      active
                        ? 'bg-alpine-neoncya-n/10 text-alpine-neon-cyan'
                        : 'text-alpine-text-secondary hover:text-alpine-text-primary hover:bg-alpine-black-primary'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-semibold">{item.label}</span>
                  </Link>
                )
              })}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <TradingEnvironmentBadge />
            <UserMenu />
          </div>
        </div>
      </div>
    </nav>
  )
}

