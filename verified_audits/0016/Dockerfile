# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY telcoin-proof-of-concept /app/repo
WORKDIR /app/repo

# Remove cache directory to avoid permission issues
RUN rm -rf cache out

# Install curl and unzip for Bun installation
RUN apt-get update && apt-get install -y curl unzip

# Install Bun and install dependencies
RUN curl -fsSL https://bun.sh/install | bash && \
    /root/.bun/bin/bun install

# Install missing Forge dependencies manually
RUN rm -rf lib .git .gitmodules && \
    git init . && \
    git config user.name "Docker" && \
    git config user.email "docker@example.com" && \
    forge install foundry-rs/forge-std && \
    forge install OpenZeppelin/openzeppelin-contracts && \
    forge install OpenZeppelin/openzeppelin-contracts-upgradeable

# Run the test
RUN forge test 

# verification = yes /w modification | Correctness = no oracle