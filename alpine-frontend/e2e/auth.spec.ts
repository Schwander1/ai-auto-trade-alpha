import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can sign up', async ({ page }) => {
    await page.goto('/signup')
    
    await page.fill('input[type="email"]', `test${Date.now()}@example.com`)
    await page.fill('input[type="password"]', 'TestPass123!')
    await page.fill('input[name="full_name"]', 'Test User')
    
    await page.click('button[type="submit"]')
    
    // Should redirect to login or dashboard
    await expect(page).toHaveURL(/\/login|\/dashboard/, { timeout: 5000 })
  })

  test('user can log in', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'TestPass123!')
    
    await page.click('button[type="submit"]')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 5000 })
  })

  test('protected routes redirect to login', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Should redirect to login if not authenticated
    await expect(page).toHaveURL(/\/login/, { timeout: 3000 })
  })
})

