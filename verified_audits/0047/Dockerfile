# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2022-12-escher /app/repo
WORKDIR /app/repo

# Run the test
RUN forge test --mt test_LPDA_getPrice_NegativePrice -vvv 