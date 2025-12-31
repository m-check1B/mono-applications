# Speak by Kraliki - Frontend Dockerfile
FROM node:22-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy application
COPY . .

# Expose port
EXPOSE 5173

# Run development server
# Note: 0.0.0.0 is safe here because container port is not exposed to host
# Only Traefik can reach it via Docker network
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
