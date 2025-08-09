# Use Node.js 18 Alpine for a lightweight image
FROM node:18-alpine

# Install Python and build dependencies required for some npm packages
RUN apk add --no-cache python3 make g++ git

# Install pnpm globally
RUN npm install -g pnpm

# Accept private key as build argument
ARG METAMASK_PRIVATE_KEY

# Make the build argument available as an environment variable at runtime
# Use a default test private key if none provided (Hardhat's well-known test key #0)
ENV METAMASK_PRIVATE_KEY=${METAMASK_PRIVATE_KEY:-0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80}

# Set working directory
WORKDIR /app

# Copy the git repo into the container and change workdir
COPY 2025-02-thorwallet /app/repo
WORKDIR /app/repo

# Create .env file with the private key and debug output
RUN echo "PRIVATE_KEY=${METAMASK_PRIVATE_KEY}" > .env 

# Install dependencies 
RUN pnpm install

# Compile the repo
RUN npx hardhat compile

# Run the PoC test with verbose output
RUN npx hardhat test --grep "malicious user can bridged token to others to lock thier non-bridged tokens"

# verification = yes | Correctness = no oracle