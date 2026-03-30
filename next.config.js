/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV !== "production";
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8055";

const config = {
  reactStrictMode: false,
  images: {
    unoptimized: true,
  },
  turbopack: {
    rules: {
      "*.svg": {
        loaders: ["@svgr/webpack"],
        as: "*.js",
      },
    },
  },
  async redirects() {
    return [];
  },
  // Proxy /.auth/* and /version.json to the backend in dev mode
  async rewrites() {
    if (!isDev) return [];
    return [
      { source: "/.auth/:path*", destination: `${apiUrl}/.auth/:path*` },
      { source: "/version.json", destination: `${apiUrl}/version.json` },
    ];
  },
  // Only static export in production
  ...(isDev ? {} : { output: "export" }),
  distDir: "./out",
};

module.exports = config;
