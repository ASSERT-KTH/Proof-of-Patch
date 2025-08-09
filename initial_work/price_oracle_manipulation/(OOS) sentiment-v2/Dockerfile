# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/sherlock-audit/2024-08-sentiment-v2.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# Set the working directory for the clone operation.
WORKDIR /app

# Clone the repository.
# --depth 1 creates a shallow clone, downloading only the latest commit.
RUN echo "Cloning repository from ${REPO_URL} into ${CLONE_DESTINATION}..." && \
    git clone --depth 1 "${REPO_URL}" "${CLONE_DESTINATION}" && \
    echo "Cloning complete."

# Set the working directory to the cloned repository.
WORKDIR /app/cloned_repo/protocol-v2

# Copy PoC into the cloned repository test environment.
COPY PoC/Sherlock.t.sol /app/cloned_repo/protocol-v2/test/Sherlock.t.sol

# Build the environment and run the test
RUN forge build
RUN ARB_RPC_URL="https://arb-mainnet.g.alchemy.com/v2/aA2nkPDT5ZcPX5S2R32XLUHNI5feX1dx" forge test --match-test "testSherlockRedstoneTimestampManipulation" --ffi -vv