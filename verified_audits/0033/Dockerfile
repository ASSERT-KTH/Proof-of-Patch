# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2023-10-nextgen /app/repo
WORKDIR /app/repo

# Run the test and install dependencies
RUN forge install foundry-rs/forge-std
RUN forge test -vvvvv --match-contract NextGenCoreTest --match-test testBurnToMintReentrancy

# verification = yes | Correctness = no oracle