# Use an official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Run as root user to avoid permission issues
USER root

# Set the working directory inside the container
WORKDIR /app

# Copy the repo into the docker environment
COPY 2023-10-PasswordStore /app/repo
WORKDIR /app/repo

# Initialize git and install forge-std
RUN git init
RUN forge install foundry-rs/forge-std

# Run the test
RUN forge test --mt test_any_non_owner_can_see_password -vvv 