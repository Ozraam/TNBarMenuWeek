# Use Bun runtime as build stage
FROM oven/bun:1 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and lock file
COPY package*.json ./
COPY bun.lockb ./

# Install dependencies
RUN bun install

# Copy the rest of the application code
COPY . .

# Build the SvelteKit app
RUN bun --bun run build

# Production stage
FROM oven/bun:1
WORKDIR /app

# Copy package.json and lock file for production dependencies
COPY package*.json ./
COPY bun.lockb ./

# Install all dependencies (some dev dependencies are needed at runtime for SvelteKit)
RUN bun install

# Copy the built application from build stage
COPY --from=build /app/build ./build

# Copy any additional files needed for runtime (if any)
COPY --from=build /app/package.json ./

# Expose the port the app runs on
EXPOSE 3000

# Command to run the app (SvelteKit with Bun adapter typically uses build/index.js)
CMD ["bun", "build/index.js"]
