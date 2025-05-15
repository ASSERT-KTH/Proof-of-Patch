# Use Node.js as the base image
FROM node:16

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2022-11-ens.git" 
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
COPY PoC/poc_ens.js /app/cloned_repo/test/wrapper/poc_ens.js

# Build the environment and run the test
RUN npx hardhat test test/wrapper/poc_ens.js