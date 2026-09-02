import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The SDK ships a wasm build; keep it out of server bundles.
  serverExternalPackages: ["@reactor-team/js-sdk", "@reactor-models/lingbot-world-2"],
};

export default nextConfig;
