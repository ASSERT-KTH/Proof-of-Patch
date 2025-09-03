# Use Node.js 18 as required by package.json
FROM node:18-alpine

# Install git for dependencies that may need it
RUN apk add --no-cache git python3 make g++

# Enable corepack to use the correct yarn version
RUN corepack enable

# Set working directory
WORKDIR /app

# Copy the entire project
COPY 2023-09-venus /app/repo
WORKDIR /app/repo

# Install dependencies
RUN yarn install

# Compile contracts
RUN yarn compile

# Run the specific test
RUN npx hardhat test tests/hardhat/Prime/Prime.ts --grep "prevent_Update"