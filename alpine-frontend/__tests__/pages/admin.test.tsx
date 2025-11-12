import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AdminPage from '@/app/admin/page'

global.fetch = jest.fn()

describe('AdminPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        total_users: 100,
        active_users: 85,
        new_users_this_month: 10,
        signals_delivered_this_month: 500,
        users_by_tier: {
          starter: 50,
          pro: 30,
          elite: 20,
        },
        api_requests_today: 1000,
        error_rate: 0.5,
      }),
    })
  })

  it('renders admin page', async () => {
    render(<AdminPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/admin dashboard/i)).toBeInTheDocument()
    })
  })

  it('displays analytics overview', async () => {
    render(<AdminPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/total users/i)).toBeInTheDocument()
      expect(screen.getByText(/active users/i)).toBeInTheDocument()
    })
  })

  it('switches to users tab', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: [
          {
            id: '1',
            email: 'user@example.com',
            tier: 'starter',
            is_active: true,
            created_at: new Date().toISOString(),
          },
        ],
      }),
    })

    render(<AdminPage />)
    
    const usersTab = screen.getByText(/users/i)
    fireEvent.click(usersTab)
    
    await waitFor(() => {
      expect(screen.getByText(/all users/i)).toBeInTheDocument()
    })
  })

  it('switches to revenue tab', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_revenue: 10000,
        mrr: 5000,
        active_subscriptions: 50,
        churn_rate: 2.5,
        revenue_by_tier: {
          starter: 2000,
          pro: 5000,
          elite: 3000,
        },
        revenue_today: 100,
        revenue_this_week: 700,
        revenue_this_month: 3000,
      }),
    })

    render(<AdminPage />)
    
    const revenueTab = screen.getByText(/revenue/i)
    fireEvent.click(revenueTab)
    
    await waitFor(() => {
      expect(screen.getByText(/\$10000/)).toBeInTheDocument()
    })
  })

  it('shows access denied for non-admin users', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 403,
    })

    render(<AdminPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/access denied/i)).toBeInTheDocument()
    })
  })
})

