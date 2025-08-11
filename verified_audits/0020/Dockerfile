# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# --- START: Install Node.js, npm, and global yarn ---
# Switch to root user to install packages.
USER root

# Install prerequisites for adding NodeSource repository and Node.js itself
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Add the NodeSource repository for Node.js LTS
ENV NODE_MAJOR 16
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# Install Node.js
RUN apt-get update && \
    apt-get install -y nodejs && \
    # Clean up apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install yarn and make globally using the now available npm
RUN npm install --global yarn
RUN apt-get update && apt-get install -y make g++ python3

# Switch back to the default foundry user for subsequent operations.
USER foundry
# --- END: Install Node.js, npm, and global yarn ---

# Set the working directory
WORKDIR /app

# Copy the entire repository into the container and change workdir
COPY --chown=foundry:foundry 2022-12-gogopool /app/repo
WORKDIR /app/repo

# Install dependencies
RUN yarn

# Build the contracts first
RUN forge build

# Run the specific test
RUN forge test --match-test testHijackMinipool -v

# Verification = yes /w modification | Correctness = no oracle