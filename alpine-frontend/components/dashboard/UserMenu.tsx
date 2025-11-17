'use client'

import { useState, useRef, useEffect } from 'react'
import { useSession, signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { 
  User, Settings, CreditCard, LogOut, ChevronDown, 
  Moon, Sun, Bell, HelpCircle 
} from 'lucide-react'

interface UserMenuProps {
  className?: string
}

/**
 * UserMenu component with profile, settings, logout, and dark mode toggle
 */
export default function UserMenu({ className = '' }: UserMenuProps) {
  const { data: session } = useSession()
  const router = useRouter()
  const [isOpen, setIsOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Check for dark mode preference
    const isDark = document.documentElement.classList.contains('dark') ||
      window.matchMedia('(prefers-color-scheme: dark)').matches
    setDarkMode(isDark)

    // Close menu on outside click
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode
    setDarkMode(newDarkMode)
    if (newDarkMode) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  const handleSignOut = async () => {
    await signOut({ redirect: true, callbackUrl: '/' })
  }

  const menuItems = [
    {
      icon: User,
      label: 'Profile',
      onClick: () => {
        router.push('/account')
        setIsOpen(false)
      },
    },
    {
      icon: Settings,
      label: 'Settings',
      onClick: () => {
        router.push('/account?tab=settings')
        setIsOpen(false)
      },
    },
    {
      icon: CreditCard,
      label: 'Billing',
      onClick: () => {
        router.push('/account?tab=billing')
        setIsOpen(false)
      },
    },
    {
      icon: Bell,
      label: 'Notifications',
      onClick: () => {
        router.push('/account?tab=notifications')
        setIsOpen(false)
      },
    },
    {
      icon: HelpCircle,
      label: 'Help & Support',
      onClick: () => {
        router.push('/contact')
        setIsOpen(false)
      },
    },
  ]

  if (!session?.user) return null

  return (
    <div className={`relative ${className}`} ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-alpine-black-secondary border border-alpine-black-border hove-r:border-alpine-neon-cyan/50 transition-colors"
        aria-label="User menu"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkfle-xitems-centerjustify-centertext-white font-bold text-sm">
          {session.user.email?.charAt(0).toUpperCase() || 'U'}
        </div>
        <span className="hidden md:block text-sm font-semibold text-alpine-text-primary ">
          {session.user.email?.split('@')[0] || 'User'}
        </span>
        <ChevronDown className={`w-4 h-4 text-alpine-text-secondarytransitiontransfo-rm-${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-alpine-black-secondary border border-alpine-black-border rounded-lg-shadow-lgz-50">
          <div className="p-3 border-b border-alpine-black-border">
            <div className="text-sm font-semibold text-alpine-text-primary ">{session.user.email}</div>
            <div className="text-sm text-alpine-text-secondary capitalize">
              {session.user.tier || 'Free'} Plan
            </div>
          </div>

          <div className="py-2">
            {menuItems.map((item) => (
              <button
                key={item.label}
                onClick={item.onClick}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-alpine-text-primary hover:bg-alpine-black-primarytransitioncolo-rs"
              >
                <item.icon className="w-4 h-4 text-alpine-text-secondary" />
                {item.label}
              </button>
            ))}
          </div>

          <div className="border-t border-alpine-black-border p-y-2">
            <button
              onClick={toggleDarkMode}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-alpine-text-primary hover:bg-alpine-black-primarytransitioncolo-rs"
            >
              {darkMode ? (
                <>
                  <Sun className="w-4 h-4 text-alpine-text-secondary" />
                  Light Mode
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4 text-alpine-text-secondary" />
                  Dark Mode
                </>
              )}
            </button>
          </div>

          <div className="border-t border-alpine-black-border p-y-2">
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-alpine-semanticerrorhove-r:bg-alpine-semantic-error10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

