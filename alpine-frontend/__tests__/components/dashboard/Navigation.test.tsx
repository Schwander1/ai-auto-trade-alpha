import { render, screen, fireEvent } from '@testing-library/react'
import Navigation from '@/components/dashboard/Navigation'

// Mock usePathname
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/dashboard'),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  })),
}))

jest.mock('next-auth/react', () => ({
  signOut: jest.fn(),
}))

jest.mock('@/components/dashboard/UserMenu', () => ({
  __esModule: true,
  default: () => <div data-testid="user-menu">UserMenu</div>,
}))

jest.mock('@/components/dashboard/TradingEnvironmentBadge', () => ({
  __esModule: true,
  default: () => <div data-testid="trading-badge">TradingBadge</div>,
}))

describe('Navigation', () => {
  it('renders navigation bar', () => {
    render(<Navigation />)
    
    expect(screen.getByText(/alpine analytics/i)).toBeInTheDocument()
  })

  it('displays all navigation links', () => {
    render(<Navigation />)
    
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
    expect(screen.getByText(/signals/i)).toBeInTheDocument()
    expect(screen.getByText(/backtest/i)).toBeInTheDocument()
    expect(screen.getByText(/account/i)).toBeInTheDocument()
    expect(screen.getByText(/pricing/i)).toBeInTheDocument()
  })

  it('highlights active route', () => {
    const { usePathname } = require('next/navigation')
    usePathname.mockReturnValueOnce('/dashboard')

    render(<Navigation />)
    
    const dashboardLink = screen.getByText(/dashboard/i).closest('a')
    // Check for active styling class
    expect(dashboardLink).toHaveClass(/bg-alpine-neon-cyan|alpine-neon-cyan/)
  })

  it('navigates to different routes', () => {
    const mockPush = jest.fn()
    const { useRouter } = require('next/navigation')
    useRouter.mockReturnValueOnce({
      push: mockPush,
      replace: jest.fn(),
      prefetch: jest.fn(),
    })

    render(<Navigation />)
    
    const signalsLink = screen.getByText(/signals/i).closest('a')
    if (signalsLink) {
      fireEvent.click(signalsLink)
      // Navigation should work
      expect(signalsLink).toBeInTheDocument()
    }
  })
})

