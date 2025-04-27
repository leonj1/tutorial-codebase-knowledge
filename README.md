# Markdown Documentation Server

A Docker-based server for rendering and serving markdown documentation files with a React and Tailwind CSS frontend.

## Features

- Responsive web interface for browsing markdown documentation
- Syntax highlighting for code blocks
- Support for Mermaid diagrams
- Dark mode toggle
- Navigation sidebar with folder structure
- Mobile-friendly design

## Prerequisites

- Docker
- Make (optional, for using the Makefile commands)

## Quick Start

### Building the Docker Image

```bash
make build
```

This will build the Docker image with all the necessary dependencies.

### Starting the Server

```bash
make start
```

This will start the Docker container and make the documentation available at http://10.1.1.144:80.

### Stopping the Server

```bash
make stop
```

This will stop and remove the running Docker container.

### Restarting the Server

```bash
make restart
```

This will stop the current container and start a new one.

### Cleaning Up

```bash
make clean
```

This will stop and remove the container, and also remove the Docker image.

## Manual Commands (without Make)

If you don't have Make installed, you can use these Docker commands directly:

### Build the Image

```bash
docker build -t markdown-docs .
```

### Start the Container

```bash
docker run -d --name markdown-docs-container -p 80:80 -e HOST_IP=10.1.1.144 markdown-docs
```

### Stop the Container

```bash
docker stop markdown-docs-container
docker rm markdown-docs-container
```

## Configuration

You can modify the following variables in the Makefile:

- `IMAGE_NAME`: The name of the Docker image (default: markdown-docs)
- `CONTAINER_NAME`: The name of the Docker container (default: markdown-docs-container)
- `PORT`: The port to expose on the host (default: 80)
- `HOST_IP`: The IP address where the server will be accessible (default: 10.1.1.144)

## Directory Structure

- `output/`: Contains the markdown files to be served
- `src/`: React application source code
- `public/`: Static assets

## License

MIT
