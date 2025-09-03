# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2024-12-numa-audit /app/repo
WORKDIR /app/repo/Numa

# Install Node.js and npm dependencies, then build project  
RUN apt-get update && apt-get install -y nodejs npm && \
    sed -i '/offline = true/d' foundry.toml && \
    sed -i 's/#viaIR = true/viaIR = true/' foundry.toml && \
    npm install --legacy-peer-deps && \
    forge build

# Accept Arbitrum RPC URL as build argument from docker-compose
ARG ARBITRUM_MAINNET
ENV URLARBI=${ARBITRUM_MAINNET}

# Run the test
RUN forge test --mt test_reentrancy_leverageStrategy -vvv

# verification = yes | Correctness = no oracle