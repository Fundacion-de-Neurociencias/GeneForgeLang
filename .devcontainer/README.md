# GeneForgeLang Development Container

This directory contains the configuration files for setting up a development container for GeneForgeLang.

## Files

- `devcontainer.json` - The main configuration file for the development container
- `Dockerfile` - The Docker image definition
- `docker-compose.yml` - Docker Compose configuration for multi-container setups
- `initialize.sh` - Shell script to initialize the development environment
- `initialize.bat` - Batch script to initialize the development environment (Windows)
- `.env` - Environment variables for the development container

## Prerequisites

- Docker Desktop
- Visual Studio Code with Remote - Containers extension
- Git

## Quick Start

1. Open the project in Visual Studio Code
2. When prompted, click "Reopen in Container"
3. Wait for the container to build and start
4. Open a terminal in VS Code and run the initialization script:
   ```bash
   ./initialize.sh
   ```
   or on Windows:
   ```cmd
   initialize.bat
   ```

## Manual Setup

If you prefer to set up the container manually:

1. Build the Docker image:
   ```bash
   docker build -t geneforgelang-dev -f .devcontainer/Dockerfile .
   ```

2. Run the container:
   ```bash
   docker run -it --rm -v ${PWD}:/workspace -p 8000:8000 -p 8080:8080 geneforgelang-dev
   ```

## Features

The development container includes:

- Python 3.13 with all project dependencies
- Node.js LTS for web development tools
- Pre-installed development tools (black, flake8, mypy, bandit, etc.)
- Git configuration
- Pre-commit hooks
- VS Code extensions for Python development
- Port forwarding for web interfaces (8000, 8080)

## Customization

You can customize the development environment by modifying:

- `devcontainer.json` - Add/remove VS Code extensions, change port mappings
- `Dockerfile` - Add system dependencies or change the base image
- `docker-compose.yml` - Add additional services (databases, etc.)
- `.env` - Modify environment variables

## Troubleshooting

If you encounter issues:

1. Ensure Docker is running
2. Check that the Remote - Containers extension is installed in VS Code
3. Try rebuilding the container with "Remote-Containers: Rebuild Container" command
4. Check the container logs with `docker logs <container_id>`

## Contributing

When making changes to the development container configuration:

1. Update the relevant files in this directory
2. Test the changes by rebuilding the container
3. Update this README if necessary
4. Commit the changes with a descriptive message
