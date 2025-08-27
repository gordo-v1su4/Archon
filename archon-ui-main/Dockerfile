# Vite dev server container (Debian base for esbuild stability)
FROM node:20-slim

WORKDIR /app

# Install system dependencies needed for some npm packages and esbuild
RUN apt-get update && apt-get install -y \
    python3 make g++ git curl \
  && rm -rf /var/lib/apt/lists/*

# Set Node memory headroom to reduce OOM/panic risk during esbuild pre-bundle
ENV NODE_OPTIONS=--max-old-space-size=2048

# Copy package files
COPY package*.json ./

# Install dependencies including dev dependencies for testing
RUN npm ci --no-audit --no-fund

# Create coverage directory with proper permissions
RUN mkdir -p /app/coverage && chmod 777 /app/coverage

# Copy source code
COPY . .

# Expose the port configured in package.json (3737)
EXPOSE 3737

# Start Vite dev server (already configured with --port 3737 --host in package.json)
CMD ["npm", "run", "dev"]
