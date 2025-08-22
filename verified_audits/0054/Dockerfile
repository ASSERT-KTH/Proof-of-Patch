# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Install Git, Node.js and npm
RUN apt-get update && apt-get install -y git curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2024-11-debita-finance-v3 /app/repo

# Initialize git submodules from project root
WORKDIR /app/repo
RUN git submodule update --init --recursive

# Move to Debita-V3-Contracts and install dependencies
WORKDIR /app/repo/Debita-V3-Contracts
RUN npm install && forge install

# Run the test
RUN forge test --mt testDOSAttack