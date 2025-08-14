# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2024-02-ai-arena /app/repo
WORKDIR /app/repo

# Run the test
RUN forge test --mt testReenterPOC -vvv 

# verification = yes | Correctness = no oracle