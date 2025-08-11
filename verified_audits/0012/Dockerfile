# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Set initial working directory
WORKDIR /app

# Copy audit repository into docker
COPY 2024-06-vultisig /app/repo
WORKDIR /app/repo

# Switch to root to fix permissions
USER root

# Ensure the out and cache directories exist and have proper permissions
RUN mkdir -p /app/repo/out /app/repo/cache && \
    chmod -R 777 /app/repo/out /app/repo/cache

# Switch back to foundry user
USER foundry

# Accept Ethereum RPC URL as build argument from docker-compose
ARG ETHEREUM_MAINNET
ENV ETH_RPC_URL=${ETHEREUM_MAINNET}

# Run the PoC test
RUN forge test --mt testClaimFeesRevert

# Verification = yes /w modification | Correctness = no oracle