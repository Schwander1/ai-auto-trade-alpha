import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SignupPage from '@/app/signup/page'

global.fetch = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('SignupPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders signup form', () => {
    render(<SignupPage />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
  })

  it('validates password requirements', async () => {
    render(<SignupPage />)
    
    const passwordInput = screen.getByLabelText(/password/i)
    fireEvent.change(passwordInput, { target: { value: 'short' } })
    fireEvent.blur(passwordInput)

    await waitFor(() => {
      expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument()
    })
  })

  it('validates password match', async () => {
    render(<SignupPage />)
    
    const passwordInput = screen.getByLabelText(/password/i)
    const confirmInput = screen.getByLabelText(/confirm password/i)

    fireEvent.change(passwordInput, { target: { value: 'Password123!' } })
    fireEvent.change(confirmInput, { target: { value: 'Different123!' } })
    fireEvent.blur(confirmInput)

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'User created successfully' }),
    })

    render(<SignupPage />)
    
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const confirmInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /sign up/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'Password123!' } })
    fireEvent.change(confirmInput, { target: { value: 'Password123!' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/signup',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('test@example.com'),
        })
      )
    })
  })

  it('displays error on signup failure', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'User already exists' }),
    })

    render(<SignupPage />)
    
    const submitButton = screen.getByRole('button', { name: /sign up/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/user already exists/i)).toBeInTheDocument()
    })
  })
})

