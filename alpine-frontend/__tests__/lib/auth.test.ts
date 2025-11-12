import { authOptions } from '@/lib/auth'
import { db } from '@/lib/db'
import bcrypt from 'bcryptjs'

jest.mock('@/lib/db', () => ({
  db: {
    user: {
      findUnique: jest.fn(),
    },
  },
}))

jest.mock('bcryptjs', () => ({
  compare: jest.fn(),
}))

describe('Auth Configuration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('has correct session strategy', () => {
    expect(authOptions.session?.strategy).toBe('jwt')
  })

  it('has credentials provider configured', () => {
    expect(authOptions.providers).toHaveLength(1)
    expect(authOptions.providers[0].id).toBe('credentials')
  })

  describe('authorize function', () => {
    it('throws error when email is missing', async () => {
      const provider = authOptions.providers[0] as any
      
      await expect(
        provider.authorize({ password: 'password123' })
      ).rejects.toThrow('Email and password are required')
    })

    it('throws error when password is missing', async () => {
      const provider = authOptions.providers[0] as any
      
      await expect(
        provider.authorize({ email: 'test@example.com' })
      ).rejects.toThrow('Email and password are required')
    })

    it('throws error when user not found', async () => {
      ;(db.user.findUnique as jest.Mock).mockResolvedValue(null)
      const provider = authOptions.providers[0] as any
      
      await expect(
        provider.authorize({
          email: 'nonexistent@example.com',
          password: 'password123',
        })
      ).rejects.toThrow('Invalid email or password')
    })

    it('throws error when password is invalid', async () => {
      ;(db.user.findUnique as jest.Mock).mockResolvedValue({
        id: '1',
        email: 'test@example.com',
        passwordHash: 'hashed_password',
        tier: 'STARTER',
      })
      ;(bcrypt.compare as jest.Mock).mockResolvedValue(false)
      
      const provider = authOptions.providers[0] as any
      
      await expect(
        provider.authorize({
          email: 'test@example.com',
          password: 'wrong_password',
        })
      ).rejects.toThrow('Invalid email or password')
    })

    it('returns user when credentials are valid', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        passwordHash: 'hashed_password',
        tier: 'STARTER',
      }
      
      ;(db.user.findUnique as jest.Mock).mockResolvedValue(mockUser)
      ;(bcrypt.compare as jest.Mock).mockResolvedValue(true)
      
      const provider = authOptions.providers[0] as any
      
      const result = await provider.authorize({
        email: 'test@example.com',
        password: 'correct_password',
      })
      
      expect(result).toEqual({
        id: '1',
        email: 'test@example.com',
        tier: 'STARTER',
      })
    })
  })
})

