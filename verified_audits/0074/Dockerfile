# Dockerfile for running specific Ethos test
FROM node:18-bullseye

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the repository
COPY 2023-02-ethos /workspace/2023-02-ethos

# Set working directory to Ethos-Core
WORKDIR /workspace/2023-02-ethos/Ethos-Core

# Install dependencies
RUN npm install

# Modify the test to use .only so only the specific test runs
RUN sed -i "s/it('does not increase F collateral even with large amount of collateral fee'/it.only('does not increase F collateral even with large amount of collateral fee'/" test/LQTYStakingFeeRewardsTest.js

# Run the specific test
#CMD ["npx", "hardhat", "test", "./test/LQTYStakingFeeRewardsTest.js"]
RUN npx hardhat test ./test/LQTYStakingFeeRewardsTest.js