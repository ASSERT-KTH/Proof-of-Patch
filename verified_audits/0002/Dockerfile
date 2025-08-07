FROM node:18

# Install dependencies (curl, bash, etc.)
RUN apt-get update && apt-get install -y curl bash

# Install snfoundry and scarb
RUN curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | bash && \
    . "$HOME/.bashrc" && \
    snfoundryup -v 0.20.0 && \
    curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh -s -- -v 2.6.5

# Set working directory
WORKDIR /app

# Copy your repo into the container
COPY 2024-08-chakra /app/repo

# Set working directory for the app
WORKDIR /app/repo

# Copy PoC.ts file
COPY PoC.ts /app/repo/solidity/handler/test/ChakraSettlementHandler.ts

# Install npm dependencies
WORKDIR /app/repo/solidity/handler

# Install dependencies and run PoC
RUN yarn
RUN npx hardhat test test/ChakraSettlementHandler.ts

# Verification = yes | Correctness = no oracle