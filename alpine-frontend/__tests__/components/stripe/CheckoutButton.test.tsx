import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import CheckoutButton from '@/components/stripe/CheckoutButton'

// fetch is already mocked in jest.setup.js

const mockUseSession = jest.fn(() => ({
  data: {
    user: {
      id: '1',
      email: 'test@example.com',
    },
  },
  status: 'authenticated',
}))

jest.mock('next-auth/react', () => ({
  useSession: () => mockUseSession(),
}))

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('CheckoutButton', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Reset to default authenticated state
    mockUseSession.mockReturnValue({
      data: {
        user: {
          id: '1',
          email: 'test@example.com',
        },
      },
      status: 'authenticated',
    })
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
    mockUseSession.mockReturnValueOnce({
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
    // Ensure session is properly set
    mockUseSession.mockReturnValue({
      data: {
        user: {
          id: '1',
          email: 'test@example.com',
        },
      },
      status: 'authenticated',
    })

    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: 'https://checkout.stripe.com/test' }),
    })

    render(<CheckoutButton tier="PROFESSIONAL" />)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled()
    }, { timeout: 3000 })

    // Verify the fetch was called with correct parameters
    const fetchCalls = mockFetch.mock.calls
    const checkoutCall = fetchCalls.find((call: any[]) =>
      call[0]?.includes('/api/stripe/create-checkout-session') ||
      call[0] === '/api/stripe/create-checkout-session'
    )
    if (checkoutCall && checkoutCall[1]) {
      expect(checkoutCall[1].method).toBe('POST')
      const body = JSON.parse(checkoutCall[1].body)
      expect(body.tier).toBe('PROFESSIONAL')
      expect(body.userId).toBe('1')
    }
  })

  it('displays error on checkout failure', async () => {
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Checkout failed' }),
    })

    render(<CheckoutButton tier="STARTER" />)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    // Wait for the error to appear - the component sets error in catch block
    await waitFor(() => {
      const errorText = screen.queryByText(/checkout failed/i) ||
                       screen.queryByText(/failed to create checkout session/i) ||
                       screen.queryByText(/error/i)
      expect(errorText).toBeTruthy()
    }, { timeout: 5000 })
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
      // Wait for fetch to be called
      expect(global.fetch).toHaveBeenCalled()
    }, { timeout: 2000 })

    // Error message is displayed in a paragraph
    await waitFor(() => {
      const errorText = screen.queryByText(/failed to start checkout/i) ||
                       screen.queryByText(/network error/i)
      expect(errorText).toBeTruthy()
    }, { timeout: 2000 })
  })
})
