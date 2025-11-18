import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AccountPage from '@/app/account/page'

global.fetch = jest.fn()

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({
    data: {
      user: {
        id: '1',
        email: 'test@example.com',
        tier: 'STARTER',
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

describe('AccountPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        tier: 'starter',
      }),
    })
  })

  it('renders account page', async () => {
    render(<AccountPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/account/i)).toBeInTheDocument()
    })
  })

  it('displays profile tab by default', async () => {
    render(<AccountPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/profile information/i)).toBeInTheDocument()
    })
  })

  it('switches to billing tab', async () => {
    render(<AccountPage />)
    
    const billingTab = screen.getByText(/billing/i)
    fireEvent.click(billingTab)
    
    await waitFor(() => {
      expect(screen.getByText(/billing & subscription/i)).toBeInTheDocument()
    })
  })

  it('switches to settings tab', async () => {
    render(<AccountPage />)
    
    const settingsTab = screen.getByText(/settings/i)
    fireEvent.click(settingsTab)
    
    await waitFor(() => {
      expect(screen.getByText(/settings/i)).toBeInTheDocument()
    })
  })

  it('updates profile information', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    })

    render(<AccountPage />)
    
    await waitFor(() => {
      const nameInput = screen.getByDisplayValue('Test User') || 
        screen.getByLabelText(/full name/i)
      if (nameInput) {
        fireEvent.change(nameInput, { target: { value: 'Updated Name' } })
      }
    })

    const saveButton = screen.getByText(/save changes/i)
    fireEvent.click(saveButton)
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/users/profile'),
        expect.objectContaining({ method: 'PUT' })
      )
    })
  })

  it('displays subscription information', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        tier: 'pro',
        price: 99,
        current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      }),
    })

    render(<AccountPage />)
    
    const billingTab = screen.getByText(/billing/i)
    fireEvent.click(billingTab)
    
    await waitFor(() => {
      expect(screen.getByText(/pro/i)).toBeInTheDocument()
    })
  })
})

