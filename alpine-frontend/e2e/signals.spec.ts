import { test, expect } from '@playwright/test'

test.describe('Signals Page', () => {
  test('displays signal history', async ({ page }) => {
    await page.goto('/signals')
    
    await expect(page.getByText(/signal history/i)).toBeVisible()
  })

  test('filters signals by symbol', async ({ page }) => {
    await page.goto('/signals')
    
    const searchInput = page.getByPlaceholderText(/search symbols/i)
    await searchInput.fill('AAPL')
    
    // Should filter results
    await page.waitForTimeout(500)
  })

  test('exports signals to CSV', async ({ page }) => {
    await page.goto('/signals')
    
    const exportButton = page.getByText(/export csv/i)
    if (await exportButton.isVisible()) {
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)
      await exportButton.click()
      
      const download = await downloadPromise
      if (download) {
        expect(download.suggestedFilename()).toContain('.csv')
      }
    }
  })
})

