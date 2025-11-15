FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy application code
COPY . .

EXPOSE 3000

# Default command (can be overridden in docker-compose)
CMD ["npm", "run", "dev"]

