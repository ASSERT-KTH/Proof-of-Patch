# Use Node.js 16 LTS
FROM node:16-alpine

# Install git and build dependencies for native modules
RUN apk add --no-cache git python3 make g++

# Set working directory
WORKDIR /app

# Copy the ENS project
COPY 2023-04-ens/ ./

# Install dependencies
RUN yarn install

# Run the specific HexUtils test with the added test cases
RUN yarn hardhat test test/utils/HexUtils.js --grep "Special cases for hexStringToBytes32()"
#CMD ["yarn", "hardhat", "test", "test/utils/HexUtils.js"]