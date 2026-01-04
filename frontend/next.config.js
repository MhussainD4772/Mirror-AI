/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: false, // Using pages directory
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Removed rewrites - we're using Next.js API routes (pages/api/*) as proxies instead
  // This is the recommended approach for Vercel deployments
}

module.exports = nextConfig
