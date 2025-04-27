# Use Node.js as the base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY vite.config.js ./
COPY index.html ./

# Build the application
RUN npm run build

# Copy markdown files
COPY output/ ./dist/docs/

# Install express for the server
RUN npm install express

# Expose port 80
EXPOSE 80

# Start the server
CMD ["npm", "start"]
