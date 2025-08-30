# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Install git and handle permissions
USER root
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment (dependencies already included in lib/)
COPY 2023-05-ajna /app/repo

# Change ownership of the entire /app directory to foundry user
RUN chown -R foundry:foundry /app

# Switch to foundry user for running commands
USER foundry

# Navigate to the ajna-core directory where the tests are
WORKDIR /app/repo/ajna-grants

# Accept Ethereum RPC URL as build argument from docker-compose
ARG ETHEREUM_MAINNET
ENV ETH_RPC_URL=${ETHEREUM_MAINNET}

# Dependencies are already included in the repo, just build the project
RUN forge build

# Run the specific test that demonstrates the vulnerability
RUN forge test --match-test testPoCTreasuryPrecisionLoss -vvv