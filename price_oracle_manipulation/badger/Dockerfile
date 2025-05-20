# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2023-10-badger.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# --- START: Install Node.js, npm, and global yarn ---
# Switch to root user to install packages.
USER root

# Install prerequisites for adding NodeSource repository and Node.js itself
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Add the NodeSource repository for Node.js LTS
ENV NODE_MAJOR 18
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# Install Node.js
RUN apt-get update && \
    apt-get install -y nodejs && \
    # Clean up apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install yarn globally using the now available npm
RUN npm install --global yarn
RUN apt-get update && apt-get install -y make g++ python3

# Switch back to the default foundry user for subsequent operations.
USER foundry
# --- END: Install Node.js, npm, and global yarn ---

# Set the working directory for the clone operation.
WORKDIR /app

# Clone the repository.
# --depth 1 creates a shallow clone, downloading only the latest commit.
RUN echo "Cloning repository from ${REPO_URL} into ${CLONE_DESTINATION}..." && \
    git clone --depth 1 "${REPO_URL}" "${CLONE_DESTINATION}" && \
    echo "Cloning complete."

# Set the working directory to the cloned repository, and install dependencies.
WORKDIR /app/cloned_repo
RUN yarn

# Set the working directory to the test environment, and copy the PoC's into the cloned repository test environment.
WORKDIR /app/cloned_repo/packages/contracts
COPY PoC-vuln/PoC-vuln.t.sol /app/cloned_repo/packages/contracts/foundry_test/PoC-vuln.t.sol

# Build the environment and run the test
RUN forge test --mp foundry_test/PoC-vuln.t.sol


COPY PoC-exploit/PoC-exploit.t.sol /app/cloned_repo/packages/contracts/foundry_test/PoC-exploit.t.sol
COPY PoC-exploit/test/PriceFeedTestnet.sol /app/cloned_repo/packages/contracts/contracts/TestContracts/testnet/PriceFeedTestnet.sol
RUN forge test --mp foundry_test/PoC-exploit.t.sol