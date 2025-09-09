# Use an official node runtime as a parent image
FROM node:18.16-alpine3.18

# Install git and build dependencies
RUN apk --no-cache add git g++ make py3-pip

# Set the working directory to /app
WORKDIR /app

# Copy the project directory
COPY 2024-01-curves /app/repo
WORKDIR /app/repo

# Install dependencies
RUN yarn install --frozen-lockfile

# Compile the contracts
RUN npx hardhat compile

# Generate ABI and TypeChain types
RUN yarn generate:abi && yarn generate:typechain

# Run the specific test
RUN npx hardhat test test/curves-erc20.ts --grep "Selling can be bricked if all other tokens are in ERC20 contract"