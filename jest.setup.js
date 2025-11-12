/**
 * Jest setup file
 * Runs before each test file
 */

// Mock environment variables
process.env.NEXT_PUBLIC_ARGO_API_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:9001'

// Suppress console warnings in tests (optional)
// global.console = {
//   ...console,
//   warn: jest.fn(),
//   error: jest.fn(),
// }

