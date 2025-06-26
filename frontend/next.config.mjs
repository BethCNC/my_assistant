/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Commented out for development - causing issues with dev server
  // output: 'export',
  // trailingSlash: true,
  // distDir: 'out',
}

export default nextConfig
