# Stripe Subscription Setup Guide

Complete guide for setting up Stripe subscriptions for Alpine Analytics.

## Prerequisites

- Stripe account (sign up at https://stripe.com)
- Access to Stripe Dashboard
- Next.js application with authentication working
- Database with Prisma configured

## Step 1: Create Products in Stripe Dashboard

1. **Log in to Stripe Dashboard**
   - Go to https://dashboard.stripe.com
   - Make sure you're in **Test mode** for development

2. **Create Product: Starter**
   - Navigate to **Products** → **Add product**
   - Name: `Alpine Analytics - Starter`
   - Description: `Starter tier subscription`
   - Pricing model: **Recurring**
   - Price: `$485.00`
   - Billing period: **Yearly**
   - Click **Save product**
   - **Copy the Price ID** (starts with `price_...`)

3. **Create Product: Professional**
   - Repeat above steps
   - Name: `Alpine Analytics - Professional`
   - Price: `$985.00`
   - Billing period: **Yearly**
   - **Copy the Price ID**

4. **Create Product: Institutional**
   - Repeat above steps
   - Name: `Alpine Analytics - Institutional`
   - Price: `$3,985.00`
   - Billing period: **Yearly**
   - **Copy the Price ID**

## Step 2: Configure 7-Day Free Trial

For each product/price:

1. **Edit the Price**
   - Click on the price you created
   - Scroll to **Trial period**
   - Set trial period: `7 days`
   - Click **Save**

**Note:** Alternatively, you can set `trial_period_days: 7` in the checkout session creation (already configured in code).

## Step 3: Get API Keys

1. **Get Secret Key**
   - Go to **Developers** → **API keys**
   - Under **Secret key**, click **Reveal test key**
   - Copy the key (starts with `sk_test_...`)
   - This is your `STRIPE_SECRET_KEY`

2. **Get Publishable Key**
   - Same page, under **Publishable key**
   - Copy the key (starts with `pk_test_...`)
   - This is your `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`

## Step 4: Set Up Webhook Endpoint

### For Local Development (using Stripe CLI)

1. **Install Stripe CLI**
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe
   
   # Linux
   # Download from https://github.com/stripe/stripe-cli/releases
   
   # Windows
   # Download from https://github.com/stripe/stripe-cli/releases
   ```

2. **Login to Stripe CLI**
   ```bash
   stripe login
   ```

3. **Forward Webhooks to Local Server**
   ```bash
   stripe listen --forward-to localhost:3000/api/stripe/webhook
   ```
   
   This will output a webhook signing secret (starts with `whsec_...`)
   - This is your `STRIPE_WEBHOOK_SECRET` for local development

### For Production

1. **Create Webhook Endpoint in Stripe Dashboard**
   - Go to **Developers** → **Webhooks**
   - Click **Add endpoint**
   - Endpoint URL: `https://yourdomain.com/api/stripe/webhook`
   - Select events to listen to:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
   - Click **Add endpoint**
   - **Copy the Signing secret** (starts with `whsec_...`)
   - This is your `STRIPE_WEBHOOK_SECRET` for production

## Step 5: Configure Environment Variables

Add to `.env.local`:

```env
# Stripe Keys
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Price IDs
STRIPE_PRICE_ID_STARTER=price_...
STRIPE_PRICE_ID_PROFESSIONAL=price_...
STRIPE_PRICE_ID_INSTITUTIONAL=price_...

# NextAuth (required for checkout redirects)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
```

## Step 6: Run Database Migration

```bash
cd alpine-frontend

# Generate Prisma Client
npx prisma generate

# Create and run migration
npx prisma migrate dev --name add_stripe_fields
```

This adds the following fields to the User model:
- `stripeCustomerId`
- `stripeSubscriptionId`
- `stripePriceId`
- `subscriptionStatus`

## Step 7: Install Dependencies

```bash
npm install
```

This installs:
- `stripe` (server-side)
- `@stripe/stripe-js` (client-side)

## Step 8: Test the Setup

1. **Start Development Server**
   ```bash
   npm run dev
   ```

2. **Start Stripe Webhook Listener** (in separate terminal)
   ```bash
   stripe listen --forward-to localhost:3000/api/stripe/webhook
   ```

3. **Test Checkout Flow**
   - Navigate to `http://localhost:3000/pricing`
   - Click "Start Free Trial" on any tier
   - Use test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any CVC
   - Any ZIP code
   - Complete checkout
   - Should redirect to dashboard with active subscription

## Step 9: Verify Webhook Events

Check Stripe CLI output or Dashboard → **Developers** → **Events** to see:
- `checkout.session.completed` - When checkout completes
- `customer.subscription.created` - When subscription is created
- `invoice.payment_succeeded` - When payment succeeds

## Step 10: Switch to Live Mode

When ready for production:

1. **Switch to Live Mode in Stripe Dashboard**
   - Toggle **Test mode** to **Live mode**

2. **Get Live API Keys**
   - Go to **Developers** → **API keys**
   - Copy live keys (start with `sk_live_...` and `pk_live_...`)

3. **Create Live Webhook Endpoint**
   - Create new webhook endpoint with production URL
   - Copy live webhook secret

4. **Update Environment Variables**
   - Update all Stripe keys in production environment
   - Update `NEXTAUTH_URL` to production URL

## Common Issues

### "Missing required Stripe environment variables"
- Check all environment variables are set in `.env.local`
- Restart dev server after adding variables

### "Invalid signature" in webhook
- Verify `STRIPE_WEBHOOK_SECRET` matches the webhook endpoint secret
- For local dev, use the secret from `stripe listen` command
- For production, use the secret from Stripe Dashboard

### "Price ID not configured for tier"
- Verify price IDs in `.env.local` match the Price IDs from Stripe Dashboard
- Check that prices are set to "Recurring" and "Yearly"

### Webhook not receiving events
- Verify webhook endpoint URL is correct
- Check that webhook is enabled in Stripe Dashboard
- For local dev, ensure `stripe listen` is running
- Check server logs for errors

### Trial not working
- Verify `trial_period_days: 7` is set in checkout session
- Check that subscription has trial period in Stripe Dashboard
- Ensure subscription status is "trialing" after checkout

## Security Best Practices

1. **Never commit `.env.local`** to version control
2. **Use different keys** for test and production
3. **Verify webhook signatures** (already implemented)
4. **Rate limit** checkout session creation (add if needed)
5. **Validate user input** on server-side (already implemented)
6. **Use HTTPS** in production (required for webhooks)

## Next Steps

- [ ] Test all subscription flows
- [ ] Test trial expiration
- [ ] Test payment failures
- [ ] Test subscription cancellation
- [ ] Test upgrades/downgrades
- [ ] Set up email notifications
- [ ] Configure Stripe Tax (optional)
- [ ] Set up dunning management
- [ ] Test with real cards in test mode

## Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Customer Portal](https://stripe.com/docs/billing/subscriptions/integrating-customer-portal)

