import type { Metadata } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'
import { Providers } from '@/components/providers'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
})

const spaceGrotesk = Space_Grotesk({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-display',
  preload: true,
})

export const metadata: Metadata = {
  title: 'Alpine Analytics LLC - Adaptive AI Trading Signals',
  description: 'The first AI trading signal platform that adapts to market conditions. 58.5% verified win rate. 20-year tested. SHA-256 verified. Built by quantitative traders.',
  keywords: 'trading signals, AI trading, adaptive trading, market regime detection, trading algorithms, Alpine Analytics LLC',
  authors: [{ name: 'Alpine Analytics LLC' }],
  openGraph: {
    title: 'Alpine Analytics - Adaptive AI for Every Market',
    description: 'The first AI trading signal platform that adapts to market conditions.',
    type: 'website',
    url: 'https://alpineanalytics.com',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Alpine Analytics - Adaptive AI for Every Market',
    description: 'The first AI trading signal platform that adapts to market conditions.',
  },
  robots: {
    index: true,
    follow: true,
  },
  metadataBase: new URL('https://alpineanalytics.com'),
  alternates: {
    canonical: '/',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} scroll-smooth`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}

