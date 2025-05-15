# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2023-09-maia.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# Set the working directory for the clone operation.
WORKDIR /app

# Clone the repository.
# --depth 1 creates a shallow clone, downloading only the latest commit.
RUN echo "Cloning repository from ${REPO_URL} into ${CLONE_DESTINATION}..." && \
    git clone --depth 1 "${REPO_URL}" "${CLONE_DESTINATION}" && \
    echo "Cloning complete."

# Set the working directory to the cloned repository.
WORKDIR "${CLONE_DESTINATION}"

# Copy PoC into the cloned repository test environment.
COPY PoC/VirtualAccount.t.sol /app/cloned_repo/test/ulysses-omnichain/VirtualAccount.t.sol

# Build the environment and run the test
RUN forge build --optimize --optimizer-runs 200 --via-ir
RUN forge test -vv --match-contract VirtualAccountTest --optimize --optimizer-runs 200 --via-ir