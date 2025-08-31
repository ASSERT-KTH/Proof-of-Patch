# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# --- START: Install Node.js and npm---
# Switch to root user to install packages.
USER root

# Install prerequisites for adding NodeSource repository and Node.js itself
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Add the NodeSource repository for Node.js LTS
ENV NODE_MAJOR 20
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# Install Node.js
RUN apt-get update && \
    apt-get install -y nodejs && \
    # Clean up apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm and turbo globally using the now available npm
RUN npm install -g pnpm
RUN npm install turbo --global
# --- END: Install Node.js, npm, and global pnpm ---

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2023-12-revolutionprotocol /app/repo

# Switch back to the default foundry user for subsequent operations.
RUN chown -R foundry:foundry /app/repo
USER foundry

WORKDIR /app/repo

# Install dependencies and Run the PoC
RUN pnpm install
RUN cd packages/revolution && forge test --match-path test/PoC.t.sol -vvv