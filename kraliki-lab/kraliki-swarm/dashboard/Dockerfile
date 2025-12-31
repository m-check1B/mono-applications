FROM node:22-alpine

WORKDIR /app

# Install build dependencies for native modules (node-pty)
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --omit=dev

# Copy built application
COPY build ./build
COPY package.json ./

# Set environment
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

# Run built Node.js server
CMD ["node", "build"]
