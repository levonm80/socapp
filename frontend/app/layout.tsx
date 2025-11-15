import type { Metadata } from 'next'
import { Space_Grotesk } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/lib/contexts/AuthContext'

const spaceGrotesk = Space_Grotesk({ 
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'AI Web Proxy Analyzer',
  description: 'Security Operations Center application for analyzing Zscaler web proxy logs',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link 
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" 
          rel="stylesheet"
        />
      </head>
      <body className={`${spaceGrotesk.className} ${spaceGrotesk.variable} font-display min-h-screen bg-background-dark`}>
        <style dangerouslySetInnerHTML={{ __html: `
          .material-symbols-outlined {
            font-variation-settings:
            'FILL' 0,
            'wght' 400,
            'GRAD' 0,
            'opsz' 24
          }
        ` }} />
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}

