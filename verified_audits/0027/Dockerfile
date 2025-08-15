# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:nightly-cd7850bfb64a4babb07bf5dd6fe5ebac664449cf

# Switch to root user to install packages.
USER root

# Install Node.js v16.16.0, yarn, and build dependencies
RUN apk add --no-cache xz python3 make g++ && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then NODE_ARCH="x64"; else NODE_ARCH="arm64"; fi && \
    wget -qO- https://nodejs.org/dist/v16.16.0/node-v16.16.0-linux-${NODE_ARCH}.tar.xz | tar -xJ -C /usr/local --strip-components=1 && \
    npm install -g yarn

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2023-01-popcorn /app/repo

# Switch back to the default foundry user for subsequent operations.
RUN chown -R foundry:foundry /app/repo
USER foundry

WORKDIR /app/repo

ARG ETHEREUM_MAINNET

# Install the needed dependencies
RUN yarn install

# Run the test
RUN forge test -m "test__claim_reentrancy" --fork-url=${ETHEREUM_MAINNET}

# verification = yes | Correctness = no oracle