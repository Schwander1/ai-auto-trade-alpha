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
        jsx: 'react',
      },
    }],
  },
  
  // Module name mapping
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  
  // Coverage configuration
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json'],
  
  // Coverage thresholds (95% minimum)
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
    'packages/**/*.{ts,tsx,js,jsx}',
    '!packages/**/*.d.ts',
    '!packages/**/*.stories.{ts,tsx,js,jsx}',
    '!packages/**/__tests__/**',
    '!packages/**/node_modules/**',
    '!packages/**/dist/**',
    '!packages/**/build/**',
  ],
  
  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
    '/.next/',
  ],
  
  // Verbose output
  verbose: true,
};

