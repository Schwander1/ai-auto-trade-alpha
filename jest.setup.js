/**
 * Jest setup file
 * Runs before each test file
 */

// Import testing library matchers
require('@testing-library/jest-dom')

// Polyfill fetch for Node.js test environment
require('whatwg-fetch')

// Mock environment variables
process.env.NEXT_PUBLIC_ARGO_API_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:9001'

// Mock Next.js modules (only if they exist)
try {
  require.resolve('next/navigation')
  jest.mock('next/navigation', () => ({
    useRouter() {
      return {
        push: jest.fn(),
        replace: jest.fn(),
        prefetch: jest.fn(),
        back: jest.fn(),
        pathname: '/',
        query: {},
        asPath: '/',
      }
    },
    usePathname() {
      return '/'
    },
    useSearchParams() {
      return new URLSearchParams()
    },
  }))
} catch (e) {
  // Module doesn't exist, skip mock
}

try {
  require.resolve('next/image')
  jest.mock('next/image', () => ({
    __esModule: true,
    default: function Image(props) {
      const React = require('react')
      return React.createElement('img', props)
    },
  }))
} catch (e) {
  // Module doesn't exist, skip mock
}

try {
  require.resolve('next/link')
  jest.mock('next/link', () => ({
    __esModule: true,
    default: function Link({ children, href, ...props }) {
      const React = require('react')
      return React.createElement('a', { href, ...props }, children)
    },
  }))
} catch (e) {
  // Module doesn't exist, skip mock
}

// Mock fetch globally (can be overridden in individual tests)
global.fetch = jest.fn()

// Mock window.location using Object.defineProperty to avoid jsdom warnings
// Note: jsdom may have issues with this, so we'll handle it per-test if needed
if (typeof window !== 'undefined') {
  try {
    Object.defineProperty(window, 'location', {
      value: {
        href: '',
        assign: jest.fn(),
        replace: jest.fn(),
        reload: jest.fn(),
        origin: 'http://localhost',
        protocol: 'http:',
        host: 'localhost',
        hostname: 'localhost',
        port: '',
        pathname: '/',
        search: '',
        hash: '',
      },
      writable: true,
      configurable: true,
    })
  } catch (e) {
    // Location may already be defined, that's okay
  }
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
}

// Mock window.matchMedia for dark mode detection
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(), // deprecated
      removeListener: jest.fn(), // deprecated
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  })
}

// Suppress console warnings in tests (optional)
// global.console = {
//   ...console,
//   warn: jest.fn(),
//   error: jest.fn(),
// }
