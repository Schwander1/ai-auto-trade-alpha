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

// Suppress console warnings in tests (optional)
// global.console = {
//   ...console,
//   warn: jest.fn(),
//   error: jest.fn(),
// }
