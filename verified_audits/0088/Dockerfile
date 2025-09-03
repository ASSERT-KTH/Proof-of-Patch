# Use the official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Switch to root to handle file operations
USER root

# Set working directory
WORKDIR /app

# Copy entire project with our modifications and fix ownership
COPY 2023-12-arcadia /app/repo
RUN chown -R foundry:foundry /app/repo

# Switch back to foundry user
USER foundry

# Set working directory to lending-v2  
WORKDIR /app/repo/lending-v2

# Set git config globally, build and run the specific PoC test
RUN git config --global init.defaultBranch main && \
    git config --global user.name "Docker" && \
    git config --global user.email "docker@example.com" && \
    git config --global --add safe.directory '*' && \
    forge build && \
    forge test --mt testVuln_reentrancyInFlashActionEnablesStealingAllProtocolFunds