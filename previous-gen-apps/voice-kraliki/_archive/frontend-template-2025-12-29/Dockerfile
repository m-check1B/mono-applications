# syntax=docker/dockerfile:1

# Build stage
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Create non-root user before copying artifacts for faster ownership handling
RUN addgroup -g 1001 -S nodejs && \
    adduser -S svelteuser -u 1001 -G nodejs

# Copy built application and node_modules from builder stage
COPY --from=builder --chown=svelteuser:nodejs /app/build ./build
COPY --from=builder --chown=svelteuser:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=svelteuser:nodejs /app/package.json ./package.json
USER svelteuser

# Expose port 3000
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode >= 200 && r.statusCode < 400 ? 0 : 1)})"

# Start the Node.js server
CMD ["node", "build/index.js"]
