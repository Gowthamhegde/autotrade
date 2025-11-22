import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'NIFTY AutoTrader',
  description: 'ML-driven algo trading platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
