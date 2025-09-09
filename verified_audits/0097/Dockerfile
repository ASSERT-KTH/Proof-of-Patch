# Use an official node runtime as a parent image  
FROM node:16-alpine

# Accept build arguments
ARG DEPLOYER_PRIVATE_KEY
ARG ALCHEMY_API_KEY

# Set environment variables from build args
ENV DEPLOYER_PRIVATE_KEY=${DEPLOYER_PRIVATE_KEY}
ENV ALCHEMY_API_KEY=${ALCHEMY_API_KEY}

# Install git and build dependencies
RUN apk --no-cache add git g++ make python3

# Set the working directory to /app
WORKDIR /app

# Copy the project directory
COPY 2022-07-fractional /app/repo
WORKDIR /app/repo

# Initialize git submodules recursively
RUN git submodule update --init --recursive

# Install dependencies
RUN npm install

# Compile the contracts
RUN npx hardhat compile

# Run the vulnerability PoC
RUN npx hardhat run scripts/poc-vulnerability.js