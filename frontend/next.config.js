/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  reactStrictMode: true,
  webpack: (config, { isServer }) => {
    // Ensure @ alias works for both client and server
    if (!config.resolve) {
      config.resolve = {};
    }
    if (!config.resolve.alias) {
      config.resolve.alias = {};
    }
    config.resolve.alias['@'] = path.resolve(__dirname, '.');
    
    // Ensure proper module resolution
    config.resolve.modules = [
      path.resolve(__dirname, '.'),
      'node_modules',
    ];
    
    return config;
  },
}

module.exports = nextConfig

