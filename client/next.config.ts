import type {NextConfig} from 'next'

const isStaticExport = process.env.NEXT_PUBLIC_OUTPUT_MODE === 'export'

const nextConfig: NextConfig = {
  output: isStaticExport ? 'export' : undefined,
  experimental: {
    optimizePackageImports: ['@chakra-ui/react'],
  }
}

export default nextConfig
