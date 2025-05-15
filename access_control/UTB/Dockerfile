# -------------------------------- NOTE -------------------------------- #
# This test will not work unless a private key is added
# to /PoC/test/.env
# The test is validated to run with a private key
# ---------------------------------------------------------------------- #

# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2024-01-decent.git" 
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
COPY PoC/UTBReceiveFromBridge.t.sol /app/cloned_repo/test/UTBReceiveFromBridge.t.sol
COPY PoC/test/.env /app/cloned_repo/.env

# Build the environment and run the test
RUN forge build
RUN forge test --match-test testUTBReceiveFromBridge_