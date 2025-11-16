FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments for Next.js public environment variables
ARG NEXT_PUBLIC_API_URL
ARG NODE_ENV=production

# Set environment variables for Next.js build (NEXT_PUBLIC_* are embedded at build time)
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NODE_ENV=${NODE_ENV}

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application code
COPY . .

# Build the application (Next.js will use NEXT_PUBLIC_* env vars from above)
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy package files
COPY package.json package-lock.json* ./

# Install production dependencies only
RUN npm ci --only=production && npm cache clean --force

# Copy built application and necessary files from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/app ./app
COPY --from=builder /app/lib ./lib
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/package.json ./

EXPOSE 3000

ENV PORT=3000

# Start the application in production mode
CMD ["npm", "run", "start"]

