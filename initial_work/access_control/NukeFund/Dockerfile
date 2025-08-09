# -------------------------------- NOTE -------------------------------- #
# This test will not work unless a private key is added
# to /PoC/test/.env
# The test is validated to run with a private key
# ---------------------------------------------------------------------- #

# Use Node.js as the base image
FROM node:20

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2024-07-traitforge.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# Install Hardhat globally
RUN npm install -g hardhat

# Set the working directory for the clone operation.
WORKDIR /app

# Clone the repository.
# --depth 1 creates a shallow clone, downloading only the latest commit.
RUN echo "Cloning repository from ${REPO_URL} into ${CLONE_DESTINATION}..." && \
    git clone --depth 1 "${REPO_URL}" "${CLONE_DESTINATION}" && \
    echo "Cloning complete."

# Set the working directory to the cloned repository.
WORKDIR "${CLONE_DESTINATION}"

# Install project-specific dependencies
# This is a crucial step!
RUN echo "Installing project dependencies..." && \
    yarn && \
    echo "Project dependencies installed."

# Copy PoC into the cloned repository test environment.
COPY PoC/NukeFund.test.ts /app/cloned_repo/test/NukeFund.test.ts
COPY PoC/test/.env /app/cloned_repo/.env

# Build the environment and run the test
RUN yarn compile
RUN yarn test test/NukeFund.test.ts