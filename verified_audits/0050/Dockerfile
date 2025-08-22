FROM node:18

# Install dependencies
RUN apt-get update && apt-get install -y curl bash git

# Set working directory
WORKDIR /app

# Copy the repo into the container and change workdir
COPY 2024-10-swan-dria /app/repo
WORKDIR /app/repo

# Install yarn dependencies
RUN yarn install

# Run the PoC test
RUN yarn test ./test/LLMOracleCoordinator.test.ts

# Found another vulnerability, in the mean value calculation, now changed it:
# Was:
#   uint256 diff = data[i] - mean;
#   sum += diff * diff;
# Now:
#   uint256 diff;
#   if (data[i] >= mean) {diff = data[i] - mean;} 
#   else {diff = mean - data[i];}
#   sum += diff * diff;