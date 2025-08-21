# Use the official Rust image as the base.
FROM rust:latest AS builder

# Set original workdir
WORKDIR /app

# This step is crucial for the linker to find '-lpython3.13'
RUN apt-get update && apt-get install -y python3.13-dev

# Copy the repo into the container and change directory
COPY 2024-11-mantra-dex /app/repo
WORKDIR /app/repo

# Run the test
RUN cargo test test_query_rewards_divide_by_zero_cause_rewards_locked