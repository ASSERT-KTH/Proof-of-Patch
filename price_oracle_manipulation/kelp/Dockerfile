# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2023-11-kelp.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# Set the working directory for the clone operation.
WORKDIR /app

# Clone the repository.
# --depth 1 creates a shallow clone, downloading only the latest commit.
RUN echo "Cloning repository from ${REPO_URL} into ${CLONE_DESTINATION}..." && \
    git clone --depth 1 "${REPO_URL}" "${CLONE_DESTINATION}" && \
    echo "Cloning complete."

# Set the working directory to the cloned repository.
WORKDIR /app/cloned_repo

# Copy PoC into the cloned repository test environment.
COPY PoC/PoC.t.sol /app/cloned_repo/test/PoC.t.sol

# Build the environment and run the test
RUN forge test --mp test/PoC.t.sol