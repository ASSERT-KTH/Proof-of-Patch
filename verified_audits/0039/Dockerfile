FROM node:18-alpine

# Install build dependencies
RUN apk add --no-cache git python3 make g++

# Set working directory
WORKDIR /app

# Copy the repository
COPY 2023-01-rabbithole/quest-protocol /app/repo

# Change to repo directory
WORKDIR /app/repo

# Install dependencies
RUN yarn install

# Compile contracts and generate typechain
RUN npx hardhat compile

# Run the specific audit test
RUN npx hardhat test test/AuditTest.spec.ts