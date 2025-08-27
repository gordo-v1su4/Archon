# Frontend production image: build with Vite and serve static assets

# 1) Builder stage
FROM node:20-slim AS builder
WORKDIR /app

# Install system dependencies needed by some npm packages
RUN apt-get update && apt-get install -y \
    python3 make g++ git curl \
  && rm -rf /var/lib/apt/lists/*

# Provide extra memory headroom for esbuild during pre-bundle
ENV NODE_OPTIONS=--max-old-space-size=2048

# Copy package files and install deps
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Copy source and build
COPY . .
RUN npm run build

# 2) Runtime stage - serve static build with a tiny HTTP server
FROM node:20-slim AS runner
WORKDIR /app

# Install a static file server
RUN npm install -g serve

# Copy built assets only
COPY --from=builder /app/dist ./dist

# Expose UI port
EXPOSE 3737

# Serve the built app (SPA fallback enabled by -s)
CMD ["serve", "-s", "dist", "-l", "3737"]
