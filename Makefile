# Variables
IMAGE_NAME = markdown-docs
CONTAINER_NAME = markdown-docs-container
PORT = 80
HOST_IP = 10.1.1.144

# Build the Docker image
build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) .

# Start the Docker container
start:
	@echo "Starting Docker container..."
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):80 -e HOST_IP=$(HOST_IP) $(IMAGE_NAME)
	@echo "Documentation server running at http://$(HOST_IP):$(PORT)"

# Stop the Docker container
stop:
	@echo "Stopping Docker container..."
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

# Restart the Docker container
restart: stop start

# Clean up
clean:
	@echo "Cleaning up..."
	-docker stop $(CONTAINER_NAME) 2>/dev/null || true
	-docker rm $(CONTAINER_NAME) 2>/dev/null || true
	-docker rmi $(IMAGE_NAME) 2>/dev/null || true

# Help
help:
	@echo "Available targets:"
	@echo "  build    - Build the Docker image"
	@echo "  start    - Start the Docker container"
	@echo "  stop     - Stop the Docker container"
	@echo "  restart  - Restart the Docker container"
	@echo "  clean    - Remove container and image"
	@echo "  help     - Show this help message"

.PHONY: build start stop restart clean help
