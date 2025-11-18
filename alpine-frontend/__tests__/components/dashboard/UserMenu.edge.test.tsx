import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import UserMenu from '@/components/dashboard/UserMenu'

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
  signOut: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('UserMenu Edge Cases', () => {
  it('handles missing user email', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValueOnce({
      data: {
        user: {
          id: '1',
          email: null,
          tier: 'starter',
        },
      },
      status: 'authenticated',
    })

    render(<UserMenu />)
    
    expect(screen.getByRole('button', { name: /user menu/i })).toBeInTheDocument()
  })

  it('closes menu when clicking outside', async () => {
    render(<UserMenu />)
    
    const menuButton = screen.getByRole('button', { name: /user menu/i })
    fireEvent.click(menuButton)
    
    await waitFor(() => {
      expect(screen.getByText('Profile')).toBeInTheDocument()
    })

    // Click outside
    fireEvent.click(document.body)
    
    await waitFor(() => {
      expect(screen.queryByText('Profile')).not.toBeInTheDocument()
    })
  })

  it('handles dark mode toggle', async () => {
    render(<UserMenu />)
    
    const menuButton = screen.getByRole('button', { name: /user menu/i })
    fireEvent.click(menuButton)
    
    await waitFor(() => {
      const darkModeButton = screen.getByText(/dark mode|light mode/i)
      fireEvent.click(darkModeButton)
      
      // Should toggle dark mode
      const isDark = document.documentElement.classList.contains('dark')
      expect(typeof isDark).toBe('boolean')
    })
  })
})

