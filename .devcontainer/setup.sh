#!/bin/bash

# Setup script to make shell scripts executable

echo "Setting up development container scripts..."

# Make shell scripts executable
chmod +x initialize.sh
chmod +x run-tests.sh

echo "Shell scripts are now executable."

# Create a symlink for easy access
ln -sf /workspace/.devcontainer/initialize.sh /usr/local/bin/gfl-init
ln -sf /workspace/.devcontainer/run-tests.sh /usr/local/bin/gfl-test

echo "Created symlinks for easy access:"
echo "  gfl-init  -> initialize the development environment"
echo "  gfl-test  -> run all tests"

echo "Setup complete!"
