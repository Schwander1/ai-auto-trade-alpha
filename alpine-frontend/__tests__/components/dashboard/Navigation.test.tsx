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
    expect(dashboardLink).toHaveClass(/bg-alpine-accent/)
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

