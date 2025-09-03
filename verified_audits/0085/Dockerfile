# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Install Node.js and Yarn
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g yarn

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2022-11-stakehouse /app/repo
WORKDIR /app/repo

# Install dependencies with yarn
RUN yarn

# Create foundry.toml with optimized settings to avoid stack too deep
RUN echo '[profile.default]' > foundry.toml && \
    echo 'src = "contracts"' >> foundry.toml && \
    echo 'out = "out"' >> foundry.toml && \
    echo 'optimizer = true' >> foundry.toml && \
    echo 'optimizer_runs = 200' >> foundry.toml && \
    echo 'via_ir = true' >> foundry.toml

# Run the test
RUN forge test -vv --match-test test_rotateLP_Exceed_maxStakingAmountPerValidator_POC