/**
 * Prisma seed script for Alpine Analytics database.
 * 
 * Creates test users with different subscription tiers.
 * 
 * Run with: npx prisma db seed
 */

import { PrismaClient, UserTier } from '@prisma/client'
import * as bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...')

  // Hash password for test users
  const hashedPassword = await bcrypt.hash('password123', 10)

  // Create test users
  const users = [
    {
      email: 'starter@alpineanalytics.com',
      passwordHash: hashedPassword,
      tier: UserTier.STARTER,
      subscriptionStart: null,
      subscriptionEnd: null,
    },
    {
      email: 'professional@alpineanalytics.com',
      passwordHash: hashedPassword,
      tier: UserTier.PROFESSIONAL,
      subscriptionStart: new Date(),
      subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
    },
    {
      email: 'institutional@alpineanalytics.com',
      passwordHash: hashedPassword,
      tier: UserTier.INSTITUTIONAL,
      subscriptionStart: new Date(),
      subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
    },
  ]

  for (const userData of users) {
    const user = await prisma.user.upsert({
      where: { email: userData.email },
      update: {},
      create: userData,
    })
    console.log(`✅ Created/updated user: ${user.email} (${user.tier})`)
  }

  console.log('✨ Seeding completed!')
  console.log('\n📝 Test credentials:')
  console.log('  Email: starter@alpineanalytics.com')
  console.log('  Password: password123')
  console.log('  Tier: STARTER')
  console.log('\n  Email: professional@alpineanalytics.com')
  console.log('  Password: password123')
  console.log('  Tier: PROFESSIONAL')
  console.log('\n  Email: institutional@alpineanalytics.com')
  console.log('  Password: password123')
  console.log('  Tier: INSTITUTIONAL')
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })

