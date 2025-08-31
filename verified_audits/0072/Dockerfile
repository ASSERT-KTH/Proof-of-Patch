# Dockerfile for running Initia Move tests
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Go (required for initiad) - auto-detect architecture
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        GOARCH="amd64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        GOARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    wget https://go.dev/dl/go1.21.0.linux-${GOARCH}.tar.gz && \
    tar -C /usr/local -xzf go1.21.0.linux-${GOARCH}.tar.gz && \
    rm go1.21.0.linux-${GOARCH}.tar.gz

# Add Go to PATH
ENV PATH="/usr/local/go/bin:${PATH}"

# Create working directory
WORKDIR /workspace

# Clone and build initiad
RUN git clone https://github.com/initia-labs/initia.git && \
    cd initia && \
    make install

# Add initiad to PATH (assuming it's installed in ~/go/bin)
ENV PATH="/root/go/bin:${PATH}"

# Copy the test environment
COPY 2025-01-initia-move /workspace/2025-01-initia-move

# Set working directory to the project
WORKDIR /workspace/2025-01-initia-move

# Run the usernames module tests with statistics
RUN initiad move test --path ./usernames-module --statistics
#CMD ["initiad", "move", "test", "--path", "./usernames-module", "--statistics"]