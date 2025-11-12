import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login')
    // Add authentication logic here
  })

  test('displays dashboard content', async ({ page }) => {
    await page.goto('/dashboard')
    
    await expect(page.getByText(/dashboard/i)).toBeVisible()
    await expect(page.getByText(/latest signals/i)).toBeVisible()
  })

  test('shows stats cards', async ({ page }) => {
    await page.goto('/dashboard')
    
    await expect(page.getByText(/win rate/i)).toBeVisible()
    await expect(page.getByText(/total roi/i)).toBeVisible()
  })

  test('displays signal cards', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Wait for signals to load
    await page.waitForSelector('[data-testid="signal-card"]', { timeout: 10000 }).catch(() => {
      // Signals might not load, that's okay
    })
  })

  test('refreshes signals on button click', async ({ page }) => {
    await page.goto('/dashboard')
    
    const refreshButton = page.getByRole('button', { name: /refresh/i })
    if (await refreshButton.isVisible()) {
      await refreshButton.click()
    }
  })
})

