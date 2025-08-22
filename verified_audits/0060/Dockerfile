# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2023-07-pooltogether /app/repo
WORKDIR /app/repo/vault

# Run the test
RUN forge test --match-test testClaimPrize_viciousHook -vv