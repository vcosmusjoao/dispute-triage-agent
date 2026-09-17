import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next.js treats 127.0.0.1 and localhost as different origins and blocks
  // dev-only resources (HMR, client chunks) from an origin not listed here -
  // without this, pages render their server shell but never hydrate when
  // opened via 127.0.0.1 instead of localhost.
  allowedDevOrigins: ["127.0.0.1", "localhost"],
};

export default nextConfig;
