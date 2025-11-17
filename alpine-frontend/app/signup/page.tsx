'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AlertCircle, Loader2, CheckCircle2 } from 'lucide-react'

/**
 * Signup page for Alpine Analytics
 */
export default function SignupPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return 'Password must be at least 8 characters'
    }
    if (!/[A-Z]/.test(pwd)) {
      return 'Password must contain at least one uppercase letter'
    }
    if (!/[a-z]/.test(pwd)) {
      return 'Password must contain at least one lowercase letter'
    }
    if (!/[0-9]/.test(pwd)) {
      return 'Password must contain at least one number'
    }
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(false)

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password strength
    const passwordError = validatePassword(password)
    if (passwordError) {
      setError(passwordError)
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || 'Failed to create account')
        return
      }

      setSuccess(true)
      
      // Redirect to login after a brief delay
      setTimeout(() => {
        router.push('/login?registered=true')
      }, 2000)
    } catch (err) {
      setError('An unexpected error occurred. Please try again.')
      console.error('Signup error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-alpine-black-primaryflex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-8 shadow-lg">
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-display font-black text-alpine-text-primarymb-2">
              Create Account
            </h1>
            <p className="text-alpine-text-secondary">
              Start your journey with Alpine Analytics
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <div className="mb-6 p-4 bg-alpine-neon-cyan/10 border border-alpine-neon-cyan/30 rounded-lg flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-alpine-neon-cyanflexshri-nk-0 mt-0.5" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-alpine-neon-cyan mb-1">Account created!</p>
                <p className="text-sm text-alpine-text-secondary">Redirecting to login...</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-alpine-semantic-error10 border border-alpine-semantic-error30 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-alpine-semantic-errorflexshri-nk-0 mt-0.5" aria-hidden="true" />
              <p className="text-sm text-alpine-semantic-error">{error}</p>
            </div>
          )}

          {/* Signup Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-alpine-text-primary mb-2">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                disabled={isLoading || success}
                autoComplete="email"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-alpine-text-primary mb-2">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={isLoading || success}
                autoComplete="new-password"
              />
              <p className="mt-1 text-sm text-alpine-text-secondary">
                Must be at least 8 characters with uppercase, lowercase, and number
              </p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-semibold text-alpine-text-primary mb-2">
                Confirm Password
              </label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={isLoading || success}
                autoComplete="new-password"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || success}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                  Creating account...
                </>
              ) : success ? (
                <>
                  <CheckCircle2 className="w-4 h-4 mr-2" aria-hidden="true" />
                  Account created!
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-alpine-text-secondary">
              Already have an account?{' '}
              <Link
                href="/login"
                className="font-semibold text-alpine-neoncyanhove-r:text-alpine-neon-pink-transitioncolor-s"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

