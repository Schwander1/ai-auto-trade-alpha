// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock environment variables
process.env.NEXT_PUBLIC_ARGO_API_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:9001'
process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY = 'pk_test_mock'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock next-auth
jest.mock('next-auth/react', () => ({
  useSession() {
    return {
      data: {
        user: {
          id: '1',
          email: 'test@example.com',
          tier: 'starter',
        },
      },
      status: 'authenticated',
    }
  },
  signIn: jest.fn(),
  signOut: jest.fn(),
  SessionProvider: ({ children }) => children,
}))

// Mock lightweight-charts (only if module exists)
try {
  require.resolve('lightweight-charts')
  jest.mock('lightweight-charts', () => ({
    createChart: jest.fn(() => ({
      addLineSeries: jest.fn(() => ({
        setData: jest.fn(),
      })),
      timeScale: jest.fn(() => ({
        fitContent: jest.fn(),
      })),
      applyOptions: jest.fn(),
      remove: jest.fn(),
    })),
  }))
} catch (e) {
  // Module not found, skip mock
}

