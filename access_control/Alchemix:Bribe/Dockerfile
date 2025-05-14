# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry

# Define build arguments for the repository URL and the clone destination path.
# You can override these during the 'docker build' command.
ARG REPO_URL="https://github.com/alchemix-finance/alchemix-v2-dao.git" 
ARG CLONE_DESTINATION="/app/cloned_repo"

# Set the working directory for the clone operation.
# This isn't strictly necessary if using absolute paths for CLONE_DESTINATION.
WORKDIR /app

# Clone the repository.
# --depth 1 creates a shallow clone, downloading only the latest commit.
# This is faster and uses less space if you don't need the full history.
# Remove --depth 1 if you need the entire history.
RUN echo "Cloning repository from ${REPO_URL} into ${CLONE_DESTINATION}..." && \
    git clone --depth 1 "${REPO_URL}" "${CLONE_DESTINATION}" && \
    echo "Cloning complete."

# (Optional) Set the working directory to the cloned repository.
WORKDIR "${CLONE_DESTINATION}"

COPY PoC/Voting.t.sol /app/cloned_repo/src/test/Voting.t.sol

RUN forge build
RUN forge test --mt testRewardTokenAddition --rpc-url https://eth-mainnet.g.alchemy.com/v2/aA2nkPDT5ZcPX5S2R32XLUHNI5feX1dx -vv