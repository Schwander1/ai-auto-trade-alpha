import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import CheckoutButton from '@/components/stripe/CheckoutButton'

// fetch is already mocked in jest.setup.js

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

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('CheckoutButton', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders button with default text', () => {
    render(<CheckoutButton tier="STARTER" />)
    
    expect(screen.getByText(/start free trial/i)).toBeInTheDocument()
  })

  it('renders custom children', () => {
    render(<CheckoutButton tier="STARTER">Custom Text</CheckoutButton>)
    
    expect(screen.getByText('Custom Text')).toBeInTheDocument()
  })

  it('redirects to signup when not authenticated', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValueOnce({
      data: null,
      status: 'unauthenticated',
    })

    const mockPush = jest.fn()
    const { useRouter } = require('next/navigation')
    useRouter.mockReturnValueOnce({ push: mockPush })

    render(<CheckoutButton tier="STARTER" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(mockPush).toHaveBeenCalledWith('/signup?redirect=/pricing')
  })

  it('creates checkout session when authenticated', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: 'https://checkout.stripe.com/test' }),
    })

    render(<CheckoutButton tier="PROFESSIONAL" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/stripe/create-checkout-session',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            tier: 'PROFESSIONAL',
            userId: '1',
          }),
        })
      )
    })
  })

  it('displays error on checkout failure', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Checkout failed' }),
    })

    render(<CheckoutButton tier="STARTER" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/checkout failed/i)).toBeInTheDocument()
    })
  })

  it('shows loading state during checkout', async () => {
    ;(global.fetch as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({ url: 'https://checkout.stripe.com/test' }),
      }), 100))
    )

    render(<CheckoutButton tier="STARTER" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(screen.getByText(/processing/i)).toBeInTheDocument()
    expect(button).toBeDisabled()
  })

  it('handles network errors', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    render(<CheckoutButton tier="STARTER" />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/failed to start checkout/i)).toBeInTheDocument()
    })
  })
})

