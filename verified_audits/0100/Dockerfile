# Use Rust nightly image to match the toolchain
FROM rustlang/rust:nightly-bullseye

# Set working directory
WORKDIR /app

# Copy the project directory
COPY 2024-08-superposition/ /app/repo

# Navigate to the pkg directory
WORKDIR /app/repo/pkg

# Install the specific nightly version specified in rust-toolchain.toml
RUN rustup toolchain install nightly-2024-07-01
RUN rustup default nightly-2024-07-01

# Navigate to seawater package specifically
WORKDIR /app/repo/pkg/seawater

# Run only the specific test we added
RUN cargo test --features="testing" ethers_suite_orchestrated_uniswap_two_breakdown -- --exact