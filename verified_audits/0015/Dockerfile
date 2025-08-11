# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2024-06-union-finance-update-2 /app/repo
WORKDIR /app/repo/union-v2-contracts

# Install build dependencies
RUN apt-get update && apt-get install -y python3 make g++ curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs
RUN npm install --ignore-scripts || true

# Remove cache directory to avoid permission issues
RUN rm -rf cache out

# Build environment - dependencies are already in lib/
# RUN forge build --force

# Run the test
RUN forge test --mt testDrainVouchFaucet -vvv 

# verification = yes /w modification | Correctness = no oracle