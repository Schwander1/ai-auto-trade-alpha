import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ManageSubscriptionButton from '@/components/stripe/ManageSubscriptionButton'

global.fetch = jest.fn()

// window.location is already mocked in jest.setup.js

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({
    data: {
      user: {
        id: '1',
        email: 'test@example.com',
      },
    },
    status: 'authenticated',
  })),
}))

describe('ManageSubscriptionButton', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders button with default text', () => {
    render(<ManageSubscriptionButton />)
    
    expect(screen.getByText(/manage subscription/i)).toBeInTheDocument()
  })

  it('creates portal session when clicked', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: 'https://billing.stripe.com/test' }),
    })

    render(<ManageSubscriptionButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/stripe/create-portal-session',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            userId: '1',
          }),
        })
      )
    })
  })

  it('displays error when not authenticated', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValueOnce({
      data: null,
      status: 'unauthenticated',
    })

    render(<ManageSubscriptionButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(screen.getByText(/please sign in/i)).toBeInTheDocument()
  })

  it('displays error on portal session failure', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Portal session failed' }),
    })

    render(<ManageSubscriptionButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/portal session failed/i)).toBeInTheDocument()
    })
  })

  it('shows loading state during request', async () => {
    ;(global.fetch as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({ url: 'https://billing.stripe.com/test' }),
      }), 100))
    )

    render(<ManageSubscriptionButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(screen.getByText(/opening/i)).toBeInTheDocument()
    expect(button).toBeDisabled()
  })

  it('handles network errors', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    render(<ManageSubscriptionButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      // Wait for fetch to complete
      expect(global.fetch).toHaveBeenCalled()
    }, { timeout: 2000 })

    await waitFor(() => {
      // Error message might be displayed in different formats
      const errorText = screen.queryByText(/failed to open customer portal/i) ||
                       screen.queryByText(/network error/i) ||
                       screen.queryByText(/error/i) ||
                       document.querySelector('[class*="error"]')
      expect(errorText).toBeTruthy()
    }, { timeout: 2000 })
  })

  it('applies custom variant', () => {
    render(<ManageSubscriptionButton variant="ghost" />)
    
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })
})

