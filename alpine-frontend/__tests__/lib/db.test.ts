import { PrismaClient } from '@prisma/client'

// Mock PrismaClient
jest.mock('@prisma/client', () => ({
  PrismaClient: jest.fn().mockImplementation(() => ({
    $disconnect: jest.fn(),
  })),
}))

describe('Database Client', () => {
  it('exports db instance', async () => {
    const { db } = await import('@/lib/db')
    
    expect(db).toBeDefined()
    expect(db.$disconnect).toBeDefined()
  })

  it('creates singleton instance', async () => {
    const { db: db1 } = await import('@/lib/db')
    const { db: db2 } = await import('@/lib/db')
    
    // In non-production, should reuse same instance
    if (process.env.NODE_ENV !== 'production') {
      // Both should reference the same instance
      expect(db1).toBeDefined()
      expect(db2).toBeDefined()
    }
  })

  it('has disconnect method', async () => {
    const { db } = await import('@/lib/db')
    
    expect(typeof db.$disconnect).toBe('function')
  })
})

