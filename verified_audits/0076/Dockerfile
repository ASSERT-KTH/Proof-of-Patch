# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2023-09-centrifuge /app/repo
WORKDIR /app/repo

# Run 1 (Testing deposit): Run the test with deposit call (line 124 active, line 127 commented)
RUN forge test --mt testDepositAtDifferentPricesPoC || true

# Modify the test file: comment out deposit call (line 124) and uncomment mint call (line 127)
RUN sed -i '124s/^        /\/\/         /' /app/repo/test/LiquidityPool.t.sol && \
    sed -i '127s/^        \/\/ /        /' /app/repo/test/LiquidityPool.t.sol

# Run 2 (Testing mint): Run the test again with mint call (line 124 commented, line 127 active)  
RUN forge test --mt testDepositAtDifferentPricesPoC || true