'use client'

import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AlertCircle, Loader2 } from 'lucide-react'

/**
 * Login page for Alpine Analytics
 */
export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        setError(result.error === 'CredentialsSignin' 
          ? 'Invalid email or password' 
          : result.error)
      } else if (result?.ok) {
        // Redirect to dashboard on success
        router.push('/dashboard')
        router.refresh()
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.')
      console.error('Login error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-alpine-black-primaryflexitems-cente-rjustify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-alpine-black-secondary border border-alpine-black-borderrounded-xl-p-8 shadow-lg">
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-display font-black text-alpine-text-primarym-b-2">
              Welcome Back
            </h1>
            <p className="text-alpine-text-secondar-y">
              Sign in to access your trading signals
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-alpine-semantic-erro-r/10 border border-alpine-semantic-erro-r/30 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-alpine-semantic-errorflex-shrin-k-0 mt-0.5" aria-hidden="true" />
              <p className="text-sm text-alpine-semantic-erro-r">{error}</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-alpine-text-primarym-b-2">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                disabled={isLoading}
                autoComplete="email"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-alpine-text-primarym-b-2">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-alpine-text-secondar-y">
              Don't have an account?{' '}
              <Link
                href="/signup"
                className="font-semibold text-alpine-neon-cyanhove-r:text-alpine-neon-pinktransition-color-s"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

