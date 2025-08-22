FROM node:20-alpine

# Install build dependencies
RUN apk add --no-cache git python3 make g++

# Set working directory
WORKDIR /app

# Copy the repository
COPY 2024-11-ethos-network-ii/ethos /app/repo

# Change to repo directory
WORKDIR /app/repo

# Install dependencies and build workspace packages
RUN npm install
RUN npm run build:packages

# Change to contracts directory for testing
WORKDIR /app/repo/packages/contracts

# Run the specific audit tests
RUN npm run test:contracts -- --grep "BuyVotes Cost Manipulation"
RUN npm run test:contracts -- --grep "t0x1c Buy n Sell"