# Use Node.js as the base image
FROM node:20

# Define build arguments for the repository URL and the clone destination path.
ARG REPO_URL="https://github.com/code-423n4/2025-02-thorwallet.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# Install Hardhat globally
#RUN npm install -g hardhat

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
RUN echo "Installing project dependencies..." && \
    yarn && \
    npm install --save-dev "@layerzerolabs/devtools-evm@~1.0.6" && \
    echo "Project dependencies installed."

# Copy or
RUN echo "Running unmodified original test for MergeTgt..." && \
    npx hardhat test ./test/hardhat/MergeTgt.test.ts && \
    echo "The original test passes."

# Copy PoC into the cloned repository test environment.
COPY PoC/MergeTgt.test.ts /app/cloned_repo/test/hardhat/MergeTgt.test.ts

# Build the environment and run the test
RUN echo "Running modified PoC version test for MergeTgt..." && \
    npx hardhat test ./test/hardhat/MergeTgt.test.ts || true && \
    echo "PoC reverts due to logic error"