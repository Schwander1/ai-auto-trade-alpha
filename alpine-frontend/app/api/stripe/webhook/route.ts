/**
 * Stripe Webhook Handler
 * Handles Stripe webhook events for subscription management
 */

import { NextRequest, NextResponse } from 'next/server'
import { headers } from 'next/headers'
import { stripe } from '@/lib/stripe'
import { db } from '@/lib/db'
import Stripe from 'stripe'

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!

export async function POST(request: NextRequest) {
  try {
    const body = await request.text()
    const headersList = await headers()
    const signature = headersList.get('stripe-signature')

    if (!signature) {
      return NextResponse.json(
        { error: 'Missing stripe-signature header' },
        { status: 400 }
      )
    }

    // Verify webhook signature
    let event: Stripe.Event
    try {
      event = stripe.webhooks.constructEvent(body, signature, webhookSecret)
    } catch (err) {
      console.error('Webhook signature verification failed:', err)
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 400 }
      )
    }

    // Handle different event types
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session

        if (session.mode === 'subscription' && session.subscription) {
          const subscription = await stripe.subscriptions.retrieve(
            session.subscription as string
          )

          const userId = session.metadata?.userId
          const tier = session.metadata?.tier

          if (!userId || !tier) {
            console.error('Missing userId or tier in checkout session metadata')
            break
          }

          // Update user with subscription details
          await db.user.update({
            where: { id: userId },
            data: {
              tier: tier as any,
              stripeSubscriptionId: subscription.id,
              stripePriceId: subscription.items.data[0]?.price.id,
              subscriptionStatus: subscription.status,
              subscriptionStart: new Date(subscription.current_period_start * 1000),
              subscriptionEnd: new Date(subscription.current_period_end * 1000),
            },
          })

          console.log(`Subscription created for user ${userId}: ${tier}`)
        }
        break
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription

        const user = await db.user.findUnique({
          where: { stripeSubscriptionId: subscription.id },
        })

        if (user) {
          // Get tier from price ID
          const priceId = subscription.items.data[0]?.price.id
          let tier = user.tier

          // Determine tier from price ID
          if (priceId === process.env.STRIPE_PRICE_ID_STARTER) {
            tier = 'STARTER'
          } else if (priceId === process.env.STRIPE_PRICE_ID_PROFESSIONAL) {
            tier = 'PROFESSIONAL'
          } else if (priceId === process.env.STRIPE_PRICE_ID_INSTITUTIONAL) {
            tier = 'INSTITUTIONAL'
          }

          await db.user.update({
            where: { id: user.id },
            data: {
              tier: tier as any,
              stripePriceId: priceId,
              subscriptionStatus: subscription.status,
              subscriptionStart: new Date(subscription.current_period_start * 1000),
              subscriptionEnd: new Date(subscription.current_period_end * 1000),
            },
          })

          console.log(`Subscription updated for user ${user.id}: ${subscription.status}`)
        }
        break
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription

        const user = await db.user.findUnique({
          where: { stripeSubscriptionId: subscription.id },
        })

        if (user) {
          await db.user.update({
            where: { id: user.id },
            data: {
              tier: 'STARTER',
              subscriptionStatus: 'canceled',
              subscriptionStart: null,
              subscriptionEnd: null,
              stripeSubscriptionId: null,
              stripePriceId: null,
            },
          })

          console.log(`Subscription canceled for user ${user.id}`)
        }
        break
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object as Stripe.Invoice

        if (invoice.subscription) {
          const user = await db.user.findFirst({
            where: { stripeSubscriptionId: invoice.subscription as string },
          })

          if (user) {
            console.log(`Payment succeeded for user ${user.id}: ${invoice.id}`)
            // You can add email notification here if needed
          }
        }
        break
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice

        if (invoice.subscription) {
          const user = await db.user.findFirst({
            where: { stripeSubscriptionId: invoice.subscription as string },
          })

          if (user) {
            console.error(`Payment failed for user ${user.id}: ${invoice.id}`)
            // Update subscription status
            await db.user.update({
              where: { id: user.id },
              data: {
                subscriptionStatus: 'past_due',
              },
            })
            // You can add email alert here if needed
          }
        }
        break
      }

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    // Always return 200 to acknowledge receipt
    return NextResponse.json({ received: true })
  } catch (error) {
    console.error('Webhook error:', error)
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    )
  }
}

// Disable body parsing for webhook route
export const runtime = 'nodejs'

