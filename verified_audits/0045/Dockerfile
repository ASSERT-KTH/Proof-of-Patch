# Use official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Switch to root user for permissions
USER root

# Set working directory
WORKDIR /app

# Copy the repository and change workdir
COPY 2024-04-panoptic /app/repo
WORKDIR /app/repo

# Get ethereum key
ARG ETHEREUM_MAINNET

# Set the required Foundry profile and build
ENV FOUNDRY_PROFILE=ci_test
RUN forge build

# Run the specific test with public RPC
RUN forge test --match-test test_success_settleLongPremium -vvv --fork-url=${ETHEREUM_MAINNET}
#CMD ["forge", "test", "--match-test", "test_success_settleLongPremium", "-vv"]