'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, Signal, BarChart3, User, 
  CreditCard, Settings, LogOut
} from 'lucide-react'
import { signOut } from 'next-auth/react'
import UserMenu from './UserMenu'

/**
 * Navigation component for dashboard pages
 */
export default function Navigation() {
  const pathname = usePathname()

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/signals', label: 'Signals', icon: Signal },
    { href: '/backtest', label: 'Backtest', icon: BarChart3 },
    { href: '/account', label: 'Account', icon: User },
    { href: '/pricing', label: 'Pricing', icon: CreditCard },
  ]

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname?.startsWith(href)
  }

  return (
    <nav className="bg-alpine-card border-b border-alpine-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="text-xl font-bold text-alpine-text">
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
                        ? 'bg-alpine-accent/10 text-alpine-accent'
                        : 'text-alpine-text-dim hover:text-alpine-text hover:bg-alpine-bg'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-semibold">{item.label}</span>
                  </Link>
                )
              })}
            </div>
          </div>
          <UserMenu />
        </div>
      </div>
    </nav>
  )
}

