/**
 * Jest configuration for frontend and shared package tests
 * Enforces 95% coverage minimum
 */

module.exports = {
  // Test environment
  testEnvironment: 'jsdom',

  // File patterns to test
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],

  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],

  // Transform files
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        module: 'commonjs',
        baseUrl: '.',
        paths: {
          '@/*': ['alpine-frontend/*'],
        },
      },
    }],
  },

  // Module name mapping - fix path aliases
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/alpine-frontend/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },

  // Coverage configuration
  collectCoverage: false, // Disable by default, enable with --coverage flag
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json'],

  // Coverage thresholds (95% minimum) - only enforced when coverage is collected
  coverageThreshold: {
    global: {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95,
    },
  },

  // Files to collect coverage from
  collectCoverageFrom: [
    'alpine-frontend/**/*.{ts,tsx,js,jsx}',
    'packages/**/*.{ts,tsx,js,jsx}',
    '!**/*.d.ts',
    '!**/*.stories.{ts,tsx,js,jsx}',
    '!**/__tests__/**',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/build/**',
    '!**/.next/**',
    '!**/e2e/**',
  ],

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  // Ignore patterns - exclude e2e tests (they use Playwright)
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
    '/.next/',
    '/e2e/',
    'e2e/',
    '\\.spec\\.ts$', // Exclude Playwright spec files
  ],


  // Verbose output
  verbose: false, // Set to false for faster output, can be overridden with --verbose

  // Transform ignore patterns
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@testing-library|whatwg-fetch))',
  ],

  // Performance optimizations
  maxWorkers: '50%', // Use half of available CPUs
  cache: true,
  cacheDirectory: '<rootDir>/.jest-cache',

  // Test timeout
  testTimeout: 10000, // 10 seconds
};
