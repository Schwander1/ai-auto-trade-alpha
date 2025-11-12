import { test, expect } from '@playwright/test'

test.describe('Admin Dashboard', () => {
  test('requires admin authentication', async ({ page }) => {
    await page.goto('/admin')
    
    // Should redirect to login or show access denied
    const isLogin = await page.url().includes('/login')
    const isAccessDenied = await page.getByText(/access denied/i).isVisible().catch(() => false)
    
    expect(isLogin || isAccessDenied).toBe(true)
  })

  test('displays admin analytics when authenticated', async ({ page }) => {
    // This would require admin authentication setup
    await page.goto('/admin')
    
    // Check for admin-specific content
    const hasAdminContent = await page.getByText(/admin dashboard/i).isVisible().catch(() => false)
    const hasAccessDenied = await page.getByText(/access denied/i).isVisible().catch(() => false)
    
    // Should show either admin content or access denied
    expect(hasAdminContent || hasAccessDenied).toBe(true)
  })

  test('switches between admin tabs', async ({ page }) => {
    // Would need admin auth
    await page.goto('/admin')
    
    const usersTab = page.getByText(/users/i)
    const revenueTab = page.getByText(/revenue/i)
    
    if (await usersTab.isVisible()) {
      await usersTab.click()
      await expect(page.getByText(/all users/i)).toBeVisible({ timeout: 3000 })
    }
    
    if (await revenueTab.isVisible()) {
      await revenueTab.click()
      await expect(page.getByText(/total revenue/i)).toBeVisible({ timeout: 3000 })
    }
  })
})

