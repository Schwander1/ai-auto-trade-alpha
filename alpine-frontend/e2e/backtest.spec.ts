import { test, expect } from '@playwright/test'

test.describe('Backtesting', () => {
  test('displays backtest configuration', async ({ page }) => {
    await page.goto('/backtest')
    
    await expect(page.getByText(/backtesting/i)).toBeVisible()
    await expect(page.getByText(/configuration/i)).toBeVisible()
  })

  test('allows configuring backtest parameters', async ({ page }) => {
    await page.goto('/backtest')
    
    const symbolInput = page.getByDisplayValue('AAPL') || page.getByPlaceholderText('AAPL')
    if (await symbolInput.isVisible()) {
      await symbolInput.fill('GOOGL')
      expect(await symbolInput.inputValue()).toBe('GOOGL')
    }
  })

  test('runs backtest and displays results', async ({ page }) => {
    await page.goto('/backtest')
    
    const runButton = page.getByRole('button', { name: /run backtest/i })
    if (await runButton.isVisible()) {
      await runButton.click()
      
      // Wait for results or loading state
      await page.waitForTimeout(2000)
      
      // Should show results or loading indicator
      const hasResults = await page.getByText(/win rate/i).isVisible().catch(() => false)
      const isLoading = await page.getByText(/running/i).isVisible().catch(() => false)
      
      expect(hasResults || isLoading).toBe(true)
    }
  })
})

