import { test, expect } from '@playwright/test'

test.describe('Pricing Page', () => {
  test('displays all pricing tiers', async ({ page }) => {
    await page.goto('/pricing')
    
    await expect(page.getByText(/founder/i)).toBeVisible()
    await expect(page.getByText(/professional/i)).toBeVisible()
    await expect(page.getByText(/institutional/i)).toBeVisible()
  })

  test('shows pricing information', async ({ page }) => {
    await page.goto('/pricing')
    
    await expect(page.getByText(/\$49/)).toBeVisible()
    await expect(page.getByText(/\$99/)).toBeVisible()
    await expect(page.getByText(/\$249/)).toBeVisible()
  })

  test('opens payment modal on upgrade', async ({ page }) => {
    await page.goto('/pricing')
    
    const upgradeButton = page.getByRole('button', { name: /upgrade/i }).first()
    if (await upgradeButton.isVisible()) {
      await upgradeButton.click()
      
      await expect(page.getByText(/proceed to checkout/i)).toBeVisible({ timeout: 2000 })
    }
  })
})

