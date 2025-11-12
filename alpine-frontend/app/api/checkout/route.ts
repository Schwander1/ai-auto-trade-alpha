/**
 * Checkout API endpoint
 * Creates Stripe checkout session from priceId
 */

import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/lib/auth'
import { stripe, validateStripeConfig } from '@/lib/stripe'
import { db } from '@/lib/db'

// Hardcoded price IDs as specified
const PRICE_IDS = {
  STARTER: 'price_1SSNCpLoDEAt72V24jylX5T0',
  PROFESSIONAL: 'price_1SSNRdLoDEAt72V2LIS5cbRI',
  INSTITUTIONAL: 'price_1SSNXhLoDEAt72V2Y2uQarct',
} as const

export async function GET(request: NextRequest) {
  try {
    validateStripeConfig()

    // Get priceId from query params
    const { searchParams } = new URL(request.url)
    const priceId = searchParams.get('priceId')

    if (!priceId) {
      return NextResponse.json(
        { error: 'Missing priceId parameter' },
        { status: 400 }
      )
    }

    // Verify priceId is valid
    const validPriceIds = Object.values(PRICE_IDS)
    if (!validPriceIds.includes(priceId as any)) {
      return NextResponse.json(
        { error: 'Invalid priceId' },
        { status: 400 }
      )
    }

    // Verify authentication
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      // Redirect to login with return URL
      return NextResponse.redirect(
        new URL(`/login?redirect=${encodeURIComponent(request.url)}`, request.url)
      )
    }

    // Get user from database
    const user = await db.user.findUnique({
      where: { id: session.user.id },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Create or retrieve Stripe customer
    let customerId = user.stripeCustomerId

    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: {
          userId: user.id,
        },
      })
      customerId = customer.id

      await db.user.update({
        where: { id: user.id },
        data: { stripeCustomerId: customerId },
      })
    }

    // Determine tier from priceId
    let tier = 'STARTER'
    if (priceId === PRICE_IDS.PROFESSIONAL) tier = 'PROFESSIONAL'
    if (priceId === PRICE_IDS.INSTITUTIONAL) tier = 'INSTITUTIONAL'

    // Create checkout session
    const checkoutSession = await stripe.checkout.sessions.create({
      customer: customerId,
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      subscription_data: {
        trial_period_days: 7,
        metadata: {
          userId: user.id,
          tier: tier,
        },
      },
      metadata: {
        userId: user.id,
        tier: tier,
      },
      success_url: `${process.env.NEXTAUTH_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXTAUTH_URL}/pricing`,
      allow_promotion_codes: true,
    })

    // Redirect to Stripe Checkout
    return NextResponse.redirect(checkoutSession.url!)
  } catch (error) {
    console.error('Checkout error:', error)
    
    if (error instanceof Error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      )
    }

    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    )
  }
}

