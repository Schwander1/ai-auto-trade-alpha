import { test, expect } from '@playwright/test'

test.describe('Account Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login')
    // Add authentication setup here
  })

  test('displays account information', async ({ page }) => {
    await page.goto('/account')
    
    await expect(page.getByText(/account/i)).toBeVisible()
    await expect(page.getByText(/profile/i)).toBeVisible()
  })

  test('updates profile information', async ({ page }) => {
    await page.goto('/account')
    
    const nameInput = page.getByLabel(/full name/i)
    if (await nameInput.isVisible()) {
      await nameInput.fill('Updated Name')
      await page.getByRole('button', { name: /save/i }).click()
      
      await expect(page.getByText(/updated successfully/i)).toBeVisible({ timeout: 5000 })
    }
  })

  test('switches between account tabs', async ({ page }) => {
    await page.goto('/account')
    
    await page.getByText(/billing/i).click()
    await expect(page.getByText(/billing & subscription/i)).toBeVisible()
    
    await page.getByText(/settings/i).click()
    await expect(page.getByText(/settings/i)).toBeVisible()
  })

  test('displays subscription information', async ({ page }) => {
    await page.goto('/account?tab=billing')
    
    await expect(page.getByText(/current plan/i)).toBeVisible({ timeout: 5000 })
  })
})

