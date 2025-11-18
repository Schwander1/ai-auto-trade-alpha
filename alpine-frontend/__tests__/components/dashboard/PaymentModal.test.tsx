import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import PaymentModal from '@/components/dashboard/PaymentModal'

global.fetch = jest.fn()

// Mock Stripe
jest.mock('@stripe/stripe-js', () => ({
  loadStripe: jest.fn(() => Promise.resolve({})),
}))

describe('PaymentModal', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // window.location is already mocked in jest.setup.js
  })

  it('renders when open', () => {
    render(
      <PaymentModal
        isOpen={true}
        onClose={jest.fn()}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
    expect(screen.getByText(/upgrade to pro/i)).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(
      <PaymentModal
        isOpen={false}
        onClose={jest.fn()}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
    expect(screen.queryByText(/upgrade to pro/i)).not.toBeInTheDocument()
  })

  it('displays tier and price', () => {
    render(
      <PaymentModal
        isOpen={true}
        onClose={jest.fn()}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
    expect(screen.getByText(/upgrade to pro/i)).toBeInTheDocument()
    expect(screen.getByText(/\$99\/month/)).toBeInTheDocument()
  })

  it('calls onClose when close button clicked', () => {
    const onClose = jest.fn()
    render(
      <PaymentModal
        isOpen={true}
        onClose={onClose}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
    const closeButton = screen.getByLabelText(/close/i)
    fireEvent.click(closeButton)
    
    expect(onClose).toHaveBeenCalled()
  })

  it('creates checkout session on proceed', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        checkout_url: 'https://checkout.stripe.com/test',
      }),
    })

    render(
      <PaymentModal
        isOpen={true}
        onClose={jest.fn()}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
    // Wait for Stripe to load and button to be enabled
    await waitFor(() => {
      const proceedButton = screen.getByText(/proceed to checkout/i)
      expect(proceedButton).toBeInTheDocument()
      expect(proceedButton).not.toBeDisabled()
    }, { timeout: 3000 })
    
    const proceedButton = screen.getByText(/proceed to checkout/i)
    fireEvent.click(proceedButton)
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/subscriptions/upgrade',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ tier: 'pro' }),
        })
      )
    }, { timeout: 3000 })
  })

  it('displays error message on failure', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        detail: 'Payment failed',
      }),
    })

    render(
      <PaymentModal
        isOpen={true}
        onClose={jest.fn()}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
    // Wait for Stripe to load and button to be enabled
    await waitFor(() => {
      const proceedButton = screen.getByText(/proceed to checkout/i)
      expect(proceedButton).toBeInTheDocument()
      expect(proceedButton).not.toBeDisabled()
    }, { timeout: 3000 })
    
    const proceedButton = screen.getByText(/proceed to checkout/i)
    fireEvent.click(proceedButton)
    
    await waitFor(() => {
      // Error should be displayed
      const errorText = screen.queryByText(/payment failed/i) ||
                       screen.queryByText(/failed to create checkout session/i) ||
                       screen.queryByText(/failed/i)
      expect(errorText).toBeTruthy()
    }, { timeout: 3000 })
  })
})

