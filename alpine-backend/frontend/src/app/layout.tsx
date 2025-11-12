export const metadata = {
  title: 'Alpine Analytics - 95%+ Win Rate Trading Signals',
  description: 'Premium trading signals with complete transparency',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{margin: 0, padding: 0, fontFamily: 'system-ui, sans-serif'}}>{children}</body>
    </html>
  )
}
