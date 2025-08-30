FROM node:20-alpine

# Install build dependencies
RUN apk add --no-cache git python3 make g++ eudev-dev libusb-dev linux-headers

# Set working directory
WORKDIR /app

# Copy the repository
COPY 2024-12-bakerfi /app/repo

# Change to repo directory
WORKDIR /app/repo

# Install dependencies and build workspace packages
RUN npm install

# Run the specific audit tests
RUN npm run test -- --grep "Withdraw is DoSed"