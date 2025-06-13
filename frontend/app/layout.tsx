import type { Metadata } from 'next'
import Link from 'next/link'
import '../styles/globals.css'
import '../styles/tokens.css'

export const metadata: Metadata = {
  title: "Beth's Assistant",
  description: 'AI Assistant with Figma Design System',
  generator: 'Beth\'s Assistant',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        {/* Navigation */}
        <nav className="fixed top-4 left-4 z-50 flex gap-2">
          <Link 
            href="/" 
            className="px-3 py-1 bg-black/50 backdrop-blur-md text-white rounded-md text-sm hover:bg-black/70 transition-all"
          >
            Main App
          </Link>
          <Link 
            href="/demo" 
            className="px-3 py-1 bg-black/50 backdrop-blur-md text-white rounded-md text-sm hover:bg-black/70 transition-all"
          >
            Component Demo
          </Link>
        </nav>
        {children}
      </body>
    </html>
  )
}
