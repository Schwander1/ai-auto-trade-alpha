'use client'

import { useSession } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import Navigation from '@/components/dashboard/Navigation'
import {
  User, Settings, CreditCard, Bell, Save, Loader2,
  AlertCircle, CheckCircle2, Mail, Lock, Trash2
} from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Account Page - Profile, settings, and billing
 */
export default function AccountPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const searchParams = useSearchParams()
  const activeTab = searchParams.get('tab') || 'profile'

  const [userData, setUserData] = useState<any>(null)
  const [subscription, setSubscription] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [profileData, setProfileData] = useState({
    fullName: '',
    email: '',
  })

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  useEffect(() => {
    const fetchData = async () => {
      if (!session) return

      try {
        const [userRes, subscriptionRes] = await Promise.all([
          fetch('/api/user/me'),
          fetch('/api/subscriptions/plan'),
        ])

        if (userRes.ok) {
          const user = await userRes.json()
          setUserData(user)
          setProfileData({
            fullName: user.full_name || '',
            email: user.email || '',
          })
        }

        if (subscriptionRes.ok) {
          const sub = await subscriptionRes.json()
          setSubscription(sub)
        }
      } catch (err) {
        console.error('Failed to fetch account data:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [session])

  const handleSaveProfile = async () => {
    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await fetch('/api/users/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to update profile')
      }

      setSuccess('Profile updated successfully')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return
    }

    const password = prompt('Please enter your password to confirm:')
    if (!password) return

    try {
      const response = await fetch('/api/users/account', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })

      if (response.ok) {
        router.push('/')
      } else {
        const data = await response.json()
        alert(data.detail || 'Failed to delete account')
      }
    } catch (err) {
      alert('Failed to delete account')
    }
  }

  if (status === 'loading' || isLoading) {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'billing', label: 'Billing', icon: CreditCard },
    { id: 'notifications', label: 'Notifications', icon: Bell },
  ]

  return (
    <div className="min-h-screen bg-alpine-black-primary">
      {/* Navigation */}
      <Navigation />

      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-4 space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                const isActive = activeTab === tab.id
                return (
                  <button
                    key={tab.id}
                    onClick={() => router.push(`/account?tab=${tab.id}`)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-alpine-neon-cyan/10 text-alpine-neon-cyan border border-alpine-neon-cyan/30'
                        : 'text-alpine-text-primary hover:bg-alpine-black-primary'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {tab.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            {activeTab === 'profile' && (
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
                <h2 className="text-xl font-bold text-alpine-text-primary mb-6">Profile Information</h2>

                {error && (
                  <div className="mb-4 p-3 bg-alpine-semantic-error/10 border border-alpine-semantic-error/30 rounded-lg text-sm text-alpine-semantic-error flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                  </div>
                )}

                {success && (
                  <div className="mb-4 p-3 bg-alpine-neon-cyan/10 border border-alpine-neon-cyan/30 rounded-lg text-sm text-alpine-neon-cyan flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    {success}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-alpine-text-secondary mb-2">Full Name</label>
                    <input
                      type="text"
                      value={profileData.fullName}
                      onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
                      className="w-full px-4 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-alpine-text-secondary mb-2">Email</label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      className="w-full px-4 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                    />
                  </div>

                  <div className="flex items-center gap-4 pt-4">
                    <Button
                      onClick={handleSaveProfile}
                      disabled={isSaving}
                      className="bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink hover:from-alpine-neon-pink hover:to-alpine-neon-cyan text-white font-bold"
                    >
                      {isSaving ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4 mr-2" />
                          Save Changes
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'billing' && (
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
                <h2 className="text-xl font-bold text-alpine-text-primary mb-6">Billing & Subscription</h2>

                {subscription && (
                  <div className="space-y-6">
                    <div className="bg-alpine-black-primary rounded-lg p-4">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <div className="text-sm text-alpine-text-secondary">Current Plan</div>
                          <div className="text-2xl font-bold text-alpine-text-primary capitalize">
                            {subscription.tier}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-alpine-text-secondary">Price</div>
                          <div className="text-2xl font-bold text-alpine-text-primary ">
                            ${subscription.price}/month
                          </div>
                        </div>
                      </div>

                      {subscription.current_period_end && (
                        <div className="text-sm text-alpine-text-secondary">
                          Renews on {new Date(subscription.current_period_end).toLocaleDateString()}
                        </div>
                      )}
                    </div>

                    <div>
                      <h3 className="text-lg font-bold text-alpine-text-primary mb-4">Invoices</h3>
                      <div className="space-y-2">
                        {/* Invoice list would go here */}
                        <div className="text-sm text-alpine-text-secondary">
                          No invoices yet
                        </div>
                      </div>
                    </div>

                    <div>
                      <Button
                        onClick={() => router.push('/pricing')}
                        className="bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink hover:from-alpine-neon-pink hover:to-alpine-neon-cyan text-white font-bold"
                      >
                        Upgrade Plan
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
                <h2 className="text-xl font-bold text-alpine-text-primary mb-6">Settings</h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-alpine-text-primary mb-4">Security</h3>
                    <div className="space-y-4">
                      <button className="w-full flex items-center justify-between p-4 bg-alpine-black-primary rounded-lg hover:bg-alpine-black-primary/80 transition-colors">
                        <div className="flex items-center gap-3">
                          <Lock className="w-5 h-5 text-alpine-text-secondary" />
                          <div className="text-left">
                            <div className="font-semibold text-alpine-text-primary ">Change Password</div>
                            <div className="text-sm text-alpine-text-secondary">Update your password</div>
                          </div>
                        </div>
                      </button>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-alpine-text-primary mb-4">Danger Zone</h3>
                    <button
                      onClick={handleDeleteAccount}
                      className="w-full flex items-center justify-between p-4 bg-alpine-semantic-error/10 border border-alpine-semantic-error/30 rounded-lg hover:bg-alpine-semantic-error20 transition-colors text-alpine-semantic-error"
                    >
                      <div className="flex items-center gap-3">
                        <Trash2 className="w-5 h-5" />
                        <div className="text-left">
                          <div className="font-semibold">Delete Account</div>
                          <div className="text-sm opacity-75">Permanently delete your account</div>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
                <h2 className="text-xl font-bold text-alpine-text-primary mb-6">Notifications</h2>
                <div className="space-y-4">
                  {/* Notification settings would go here */}
                  <div className="text-alpine-text-secondary">
                    Notification preferences coming soon
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
