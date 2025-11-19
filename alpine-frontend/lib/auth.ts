import type { NextAuthOptions } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { PrismaAdapter } from "@next-auth/prisma-adapter"
import { db } from "@/lib/db"
import bcrypt from "bcryptjs"

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(db),
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Email and password are required')
        }
        const user = await db.user.findUnique({
          where: { email: credentials.email },
          include: {
            roles: {
              include: {
                permissions: true
              }
            }
          }
        })
        if (!user) {
          throw new Error('Invalid email or password')
        }
        const isValid = await bcrypt.compare(credentials.password, user.passwordHash)
        if (!isValid) {
          throw new Error('Invalid email or password')
        }

        // Check if user is admin
        const isAdmin = user.roles?.some((role: any) => role.name === 'admin') || false

        return {
          id: user.id,
          email: user.email,
          tier: user.tier,
          isAdmin: isAdmin,
        }
      }
    })
  ],
  session: {
    strategy: "jwt"
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.isAdmin = (user as any).isAdmin
        token.tier = (user as any).tier
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).isAdmin = token.isAdmin
        (session.user as any).tier = token.tier
      }
      return session
    }
  },
  pages: {
    signIn: '/login',
  }
}
