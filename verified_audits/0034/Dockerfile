# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2025-02-yieldoor /app/repo
WORKDIR /app/repo/yieldoor

ARG ETHEREUM_MAINNET

# Run the test
RUN forge test --rpc-url=${ETHEREUM_MAINNET}  --match-test test_cantClaimLiquidationFee --fork-block-number 21926708 -vvv