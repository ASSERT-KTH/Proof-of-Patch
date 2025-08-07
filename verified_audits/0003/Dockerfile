# Use Node.js 18 Alpine for a lightweight image
FROM node:18-alpine

# Install Python and build dependencies required for some npm packages
RUN apk add --no-cache python3 make g++ git

# Set working directory
WORKDIR /app

# Copy the entire 2024-08-winnables-raffles directory, as well as the PoC
COPY 2024-08-winnables-raffles /app/repo
COPY PoC.js /app/repo/public-contracts/test/TicketManager.js

# Change to the public-contracts directory
WORKDIR /app/repo/public-contracts

# Install dependencies using yarn
RUN yarn install

# Run the TicketManager.js test
RUN yarn hardhat test test/TicketManager.js --grep "Should be able to propagate when the winner is drawn"

# Verification = exceeded | Correctness = no oracle