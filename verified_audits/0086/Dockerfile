# Use the official Foundry image
FROM ghcr.io/foundry-rs/foundry:latest

# Switch to root to handle file operations
USER root

# Set working directory
WORKDIR /app

# Copy entire project with our modifications and fix ownership
COPY 2023-12-arcadia /app/repo
RUN chown -R foundry:foundry /app/repo

# Switch back to foundry user
USER foundry

# Set working directory to lending-v2  
WORKDIR /app/repo/lending-v2

# Set git config globally, build accounts-v2 submodule first, debug artifacts, then build main project and run test
RUN git config --global init.defaultBranch main && \
    git config --global user.name "Docker" && \
    git config --global user.email "docker@example.com" && \
    git config --global --add safe.directory '*' && \
    cd lib/accounts-v2 && forge build && cd ../.. && \
    echo "=== Accounts-v2 artifacts ===" && \
    find lib/accounts-v2/out -name "*UniswapV3FactoryExtension*" 2>/dev/null || echo "No UniswapV3FactoryExtension artifacts found in accounts-v2" && \
    cp -r lib/accounts-v2/out/* out/ 2>/dev/null || true && \
    forge build && \
    echo "=== Main project artifacts ===" && \
    find out -name "*UniswapV3FactoryExtension*" 2>/dev/null || echo "No UniswapV3FactoryExtension artifacts found in main out" && \
    forge test --mt testVuln_borrowUsingUndercollateralizedUniswapPosition -vvvvv