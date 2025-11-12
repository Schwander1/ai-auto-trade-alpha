# Stripe Testing Guide

Complete testing guide for Stripe subscription functionality.

## Test Card Numbers

Use these test card numbers in Stripe test mode:

### Successful Payments

- **Visa**: `4242 4242 4242 4242`
- **Visa (debit)**: `4000 0566 5566 5556`
- **Mastercard**: `5555 5555 5555 4444`
- **American Express**: `3782 822463 10005`
- **Discover**: `6011 1111 1111 1117`

**Card Details:**
- **Expiry**: Any future date (e.g., `12/34`)
- **CVC**: Any 3 digits (e.g., `123`)
- **ZIP**: Any 5 digits (e.g., `12345`)

### Declined Cards

- **Card declined**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`
- **Lost card**: `4000 0000 0000 9987`
- **Stolen card**: `4000 0000 0000 9979`
- **Processing error**: `4000 0000 0000 0119`

## Testing Checklist

### 1. Checkout Flow

- [ ] **Navigate to pricing page**
  - Go to `/pricing`
  - Verify all three tiers are displayed
  - Verify prices are correct
  - Verify "7-day free trial" is mentioned

- [ ] **Start checkout (unauthenticated)**
  - Click "Start Free Trial" without being logged in
  - Should redirect to signup/login
  - After login, should redirect back to pricing

- [ ] **Start checkout (authenticated)**
  - Login first
  - Go to `/pricing`
  - Click "Start Free Trial" on any tier
  - Should redirect to Stripe Checkout
  - Verify correct price is shown
  - Verify trial period is mentioned

- [ ] **Complete checkout**
  - Use test card: `4242 4242 4242 4242`
  - Enter card details
  - Click "Subscribe"
  - Should redirect to `/dashboard?session_id=...`
  - Verify subscription is active in dashboard

### 2. Subscription Status

- [ ] **Check dashboard after checkout**
  - Subscription status should show "Trial"
  - Tier should match selected tier
  - Trial days remaining should be visible
  - "Manage Subscription" button should be visible

- [ ] **Verify database**
  - Check `users` table
  - `subscriptionStatus` should be "trialing"
  - `tier` should match selected tier
  - `stripeCustomerId` should be set
  - `stripeSubscriptionId` should be set
  - `subscriptionStart` and `subscriptionEnd` should be set

### 3. Webhook Events

Test each webhook event:

- [ ] **checkout.session.completed**
  - Complete a checkout
  - Check Stripe CLI or Dashboard → Events
  - Verify event was received
  - Verify user was updated in database

- [ ] **customer.subscription.updated**
  - Update subscription in Stripe Dashboard
  - Change tier or price
  - Verify webhook received
  - Verify user updated in database

- [ ] **customer.subscription.deleted**
  - Cancel subscription in Stripe Dashboard
  - Verify webhook received
  - Verify user tier reset to STARTER
  - Verify subscription fields cleared

- [ ] **invoice.payment_succeeded**
  - Wait for trial to end (or manually trigger)
  - Verify payment succeeded
  - Verify webhook received
  - Verify subscription status is "active"

- [ ] **invoice.payment_failed**
  - Use declined card: `4000 0000 0000 0002`
  - Or simulate failure in Stripe Dashboard
  - Verify webhook received
  - Verify subscription status is "past_due"

### 4. Trial Period

- [ ] **Trial start**
  - Complete checkout
  - Verify status is "trialing"
  - Verify trial days remaining is 7

- [ ] **Trial expiration (simulated)**
  - In Stripe Dashboard, go to subscription
  - Click "..." → "End trial"
  - Verify subscription converts to active
  - Verify payment is charged
  - Check dashboard shows "Active" status

### 5. Customer Portal

- [ ] **Access portal**
  - Click "Manage Subscription" in dashboard
  - Should redirect to Stripe Customer Portal
  - Verify can see subscription details

- [ ] **Update payment method**
  - In portal, update payment method
  - Use new test card
  - Verify update succeeds

- [ ] **View invoices**
  - In portal, view invoice history
  - Verify invoices are listed
  - Verify can download receipts

- [ ] **Cancel subscription**
  - In portal, cancel subscription
  - Verify cancellation succeeds
  - Verify webhook received
  - Verify user updated in database

### 6. Subscription Management

- [ ] **Upgrade subscription**
  - User on STARTER tier
  - Click "Upgrade to Professional"
  - Complete checkout
  - Verify tier updated to PROFESSIONAL
  - Verify proration applied (check Stripe Dashboard)

- [ ] **Downgrade subscription**
  - User on PROFESSIONAL tier
  - In Customer Portal, change plan
  - Verify tier updated
  - Verify proration applied

### 7. Payment Failures

- [ ] **Failed payment**
  - Use declined card: `4000 0000 0000 0002`
  - Complete checkout (will fail)
  - Or wait for payment retry
  - Verify subscription status is "past_due"
  - Verify error handling works

- [ ] **Payment recovery**
  - Update payment method in portal
  - Use valid card: `4242 4242 4242 4242`
  - Verify payment succeeds
  - Verify subscription status returns to "active"

### 8. Edge Cases

- [ ] **Multiple checkout attempts**
  - Start checkout, then cancel
  - Start checkout again
  - Verify no duplicate subscriptions

- [ ] **Expired session**
  - Start checkout
  - Wait for session to expire
  - Try to complete
  - Verify error handling

- [ ] **Invalid tier**
  - Try to checkout with invalid tier
  - Verify error message

- [ ] **Unauthorized access**
  - Try to access checkout API without auth
  - Verify 401 error

## Testing with Stripe CLI

### Listen to Webhooks

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

### Trigger Test Events

```bash
# Trigger checkout.session.completed
stripe trigger checkout.session.completed

# Trigger customer.subscription.updated
stripe trigger customer.subscription.updated

# Trigger invoice.payment_failed
stripe trigger invoice.payment_failed
```

### View Events

```bash
# List recent events
stripe events list

# View specific event
stripe events retrieve evt_...
```

## Testing in Stripe Dashboard

### Simulate Trial End

1. Go to **Customers** → Select customer
2. Click on subscription
3. Click **"..."** → **"End trial"**
4. Verify subscription converts to active

### Simulate Payment Failure

1. Go to **Customers** → Select customer
2. Click on subscription
3. Click **"..."** → **"Simulate payment failure"**
4. Verify subscription status changes

### Test Subscription Updates

1. Go to **Customers** → Select customer
2. Click on subscription
3. Click **"Update subscription"**
4. Change plan or price
5. Verify webhook received

## End-to-End Test Flow

### Complete User Journey

1. **Signup**
   - Create new account at `/signup`
   - Verify account created

2. **View Pricing**
   - Navigate to `/pricing`
   - Verify all tiers visible

3. **Start Trial**
   - Click "Start Free Trial" on Professional tier
   - Complete Stripe Checkout
   - Use test card: `4242 4242 4242 4242`

4. **Verify Subscription**
   - Redirected to dashboard
   - Verify subscription status shows "Trial"
   - Verify tier is "Professional"
   - Verify 7 days remaining

5. **Access Signals**
   - Navigate to `/dashboard`
   - Verify signals are loading
   - Verify can access protected routes

6. **Manage Subscription**
   - Click "Manage Subscription"
   - Verify Customer Portal opens
   - View subscription details

7. **Trial Expiration**
   - Simulate trial end in Stripe Dashboard
   - Verify payment charged
   - Verify status changes to "Active"

8. **Upgrade**
   - Click "Upgrade to Institutional"
   - Complete checkout
   - Verify tier updated
   - Verify proration applied

9. **Cancel**
   - Open Customer Portal
   - Cancel subscription
   - Verify tier reset to STARTER
   - Verify subscription fields cleared

## Debugging

### Check Webhook Logs

```bash
# View webhook events in Stripe CLI
stripe events list

# View specific webhook
stripe events retrieve evt_...
```

### Check Server Logs

```bash
# View Next.js server logs
# Check for webhook processing errors
# Check for database update errors
```

### Check Database

```bash
# Use Prisma Studio
npx prisma studio

# Check users table
# Verify subscription fields are updated
```

### Common Issues

1. **Webhook not received**
   - Check webhook endpoint URL
   - Verify `stripe listen` is running (local)
   - Check webhook secret matches

2. **Subscription not updating**
   - Check webhook handler logs
   - Verify database connection
   - Check user ID in metadata

3. **Trial not working**
   - Verify `trial_period_days` in checkout
   - Check subscription in Stripe Dashboard
   - Verify subscription status

4. **Payment failures**
   - Check card number
   - Verify test mode is enabled
   - Check Stripe Dashboard for errors

## Production Testing

Before going live:

1. **Test with real cards** (in test mode)
2. **Verify webhook endpoint** is accessible
3. **Test all subscription flows**
4. **Test payment failures**
5. **Test cancellation**
6. **Verify email receipts** are sent
7. **Test Customer Portal** functionality
8. **Load test** checkout flow

## Success Criteria

✅ All test cases pass
✅ Webhooks are received and processed
✅ Database is updated correctly
✅ User experience is smooth
✅ Error handling works
✅ Security is maintained
✅ Performance is acceptable

