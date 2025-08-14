# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:nightly-5b7e4cb3c882b28f3c32ba580de27ce7381f415a

# Switch to root user to install packages.
USER root

# Install Node.js and npm using Alpine's package manager
RUN apk add --no-cache nodejs npm

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2024-05-predy /app/repo

# Switch back to the default foundry user for subsequent operations.
RUN chown -R foundry:foundry /app/repo
USER foundry

WORKDIR /app/repo

# Install the needed dependencies
RUN npm i

# Run the test
RUN forge test --match-test test_audit_LiquidateBlacklist  -vvvv

# verification = yes | Correctness = no oracle