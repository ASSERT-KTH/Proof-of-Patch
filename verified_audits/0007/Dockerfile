# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY --chown=root:root NextGen-Setup /app/repo
WORKDIR /app/repo

# Remove cache directory to avoid permission issues
RUN rm -rf cache out

# Build environment - dependencies are already in lib/
RUN forge build --force

# Run the test
RUN forge test --mt testMintAllTheCollection -vvv 

# verification = yes /w modification | Correctness = no oracle