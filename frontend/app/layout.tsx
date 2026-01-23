import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Network Architecture Design System',
  description: 'AI-powered network architecture design and validation platform',
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
