FROM node:18

# Install dependencies
RUN apt-get update && apt-get install -y curl bash git

# Set working directory
WORKDIR /app

# Copy the repo into the container and change workdir
COPY 2024-10-swan-dria /app/repo
WORKDIR /app/repo

# Copy the custom test file to overwrite the original
COPY LLMOracleCoordinator.test.ts test/LLMOracleCoordinator.test.ts

# Install yarn dependencies
RUN yarn install

# Run all LLMOracleCoordinator tests to ensure proper setup
RUN npx hardhat test test/LLMOracleCoordinator.test.ts

# Verification = yes /w modification | Correctness = correct