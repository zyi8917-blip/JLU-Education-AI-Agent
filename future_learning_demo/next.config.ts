import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    externalDir: true,
  },
  transpilePackages: ["scene-content-kit"],
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
