# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2024-06-new-scope /app/repo
WORKDIR /app/repo/zerolend-one

# Install dependencies with specific versions
RUN forge install OpenZeppelin/openzeppelin-contracts@v4.9.0
RUN forge install OpenZeppelin/openzeppelin-contracts-upgradeable@v4.9.0

# Debug what got installed
RUN echo "=== Lib directory ===" && ls -la lib/
RUN echo "=== OpenZeppelin contracts ===" && ls -la lib/openzeppelin-contracts/ || echo "Not found"

# Generate and show remappings
RUN forge remappings > remappings.txt
RUN echo "=== Generated remappings ===" && cat remappings.txt

# Also add manual remappings to be sure
RUN echo "@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/" >> remappings.txt
RUN echo "@openzeppelin/contracts-upgradeable/=lib/openzeppelin-contracts-upgradeable/contracts/" >> remappings.txt
RUN echo "node_modules/@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/" >> remappings.txt
RUN echo "=== Final remappings ===" && cat remappings.txt

# Remove cache directory to avoid permission issues
RUN rm -rf cache out

# Run the test directly (build will happen automatically if needed)
RUN forge test --match-path test/PoC/PoC.t.sol

# verification = yes /w modification | Correctness = no oracle