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
      <head>
        <link rel="icon" href="/assets/smiley.svg" type="image/svg+xml" />
      </head>
      <body>
        <div className="flex flex-col md:flex-row min-h-screen w-full">
          {/* Navigation - removed all nav links */}
          <div className="flex-1 flex flex-col pt-14 md:pt-0">{children}</div>
        </div>
      </body>
    </html>
  )
}
