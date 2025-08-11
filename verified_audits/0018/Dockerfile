FROM node:18

# Install dependencies
RUN apt-get update && apt-get install -y curl bash git

# Set working directory
WORKDIR /app

# Copy the repo into the container
COPY 2024-08-winnables-raffles /app/repo

# Set working directory for the contracts
WORKDIR /app/repo/public-contracts

# Install npm dependencies
RUN npm install

# Run the specific test for buyer cancellation
RUN npx hardhat test test/PoC.js

# Verification = yes | Correctness = no oracle