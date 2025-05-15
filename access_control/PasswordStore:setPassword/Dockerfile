# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/Cyfrin/2023-10-PasswordStore.git" 
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

# Install forge-std
RUN forge install foundry-rs/forge-std --no-git

# Copy PoC into the cloned repository test environment.
COPY PoC/PasswordStore.t.sol /app/cloned_repo/test/PasswordStore.t.sol

# Build the environment and run the test
RUN forge build
RUN forge test --mt test_poc_non_owner_set_password