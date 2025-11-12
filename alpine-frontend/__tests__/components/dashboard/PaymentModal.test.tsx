import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import PaymentModal from '@/components/dashboard/PaymentModal'

global.fetch = jest.fn()

describe('PaymentModal', () => {
  beforeEach(() => {
    jest.clearAllMocks()
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

    // Mock window.location
    delete (window as any).location
    window.location = { href: '' } as any

    render(
      <PaymentModal
        isOpen={true}
        onClose={jest.fn()}
        tier="pro"
        price={99}
        priceId="price_123"
      />
    )
    
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
    })
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
    
    const proceedButton = screen.getByText(/proceed to checkout/i)
    fireEvent.click(proceedButton)
    
    await waitFor(() => {
      expect(screen.getByText(/payment failed/i)).toBeInTheDocument()
    })
  })
})

