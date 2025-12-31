FROM node:22-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application
COPY . .

# Build for production
RUN npm run build

# Expose port
EXPOSE 5176

# Serve the production build
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5176"]
