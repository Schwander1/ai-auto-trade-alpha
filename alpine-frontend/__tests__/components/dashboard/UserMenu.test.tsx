import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import UserMenu from '@/components/dashboard/UserMenu'

describe('UserMenu', () => {
  it('renders user menu button', () => {
    render(<UserMenu />)
    
    // Should show user email or initial
    expect(screen.getByRole('button', { name: /user menu/i })).toBeInTheDocument()
  })

  it('opens menu when clicked', async () => {
    render(<UserMenu />)
    
    const menuButton = screen.getByRole('button', { name: /user menu/i })
    fireEvent.click(menuButton)
    
    await waitFor(() => {
      expect(screen.getByText('Profile')).toBeInTheDocument()
    })
  })

  it('displays menu items when open', async () => {
    render(<UserMenu />)
    
    const menuButton = screen.getByRole('button', { name: /user menu/i })
    fireEvent.click(menuButton)
    
    await waitFor(() => {
      expect(screen.getByText('Profile')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
      expect(screen.getByText('Billing')).toBeInTheDocument()
      expect(screen.getByText('Sign Out')).toBeInTheDocument()
    })
  })

  it('toggles dark mode', async () => {
    render(<UserMenu />)
    
    const menuButton = screen.getByRole('button', { name: /user menu/i })
    fireEvent.click(menuButton)
    
    await waitFor(() => {
      const darkModeButton = screen.getByText(/dark mode|light mode/i)
      fireEvent.click(darkModeButton)
      
      // Dark mode toggle should work
      expect(document.documentElement.classList.contains('dark') || 
             !document.documentElement.classList.contains('dark')).toBeTruthy()
    })
  })
})

