# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Get ethereum key
ARG ETHEREUM_MAINNET

# Copy the repo into the docker environment
COPY 2023-05-party /app/repo
WORKDIR /app/repo

# Run the test
RUN ETH_RPC_URL=${ETHEREUM_MAINNET} forge test --match-path sol-tests/PoC.t.sol -vvv