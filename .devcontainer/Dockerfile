# Use the official Python image as the base image
FROM mcr.microsoft.com/vscode/devcontainers/python:3.13-bullseye

# [Choice] Node.js version: none, lts/*, 16, 14
ARG NODE_VERSION="lts/*"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    libffi-dev \
    libssl-dev \
    docker.io \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN if [ "$USER_GID" != "1000" ] || [ "$USER_UID" != "1000" ]; then \
        groupmod --gid $USER_GID $USERNAME \
        && usermod --uid $USER_UID --gid $USER_GID $USERNAME \
        && chown -R $USER_UID:$USER_GID /home/$USERNAME; \
    fi

# Set the working directory
WORKDIR /workspace

# Copy requirements files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -e .[full] \
    && pip install pre-commit

# Install additional tools for development
RUN pip install \
    black \
    flake8 \
    mypy \
    bandit \
    safety \
    ruff

# Create symbolic links for common commands
RUN ln -s /usr/local/bin/python /usr/bin/python3 || true

# Copy devcontainer scripts
COPY .devcontainer/*.sh .devcontainer/
RUN chmod +x *.sh

# Set the default user
USER $USERNAME

# Set the default shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Expose ports
EXPOSE 8000 8080

# Set the default command
CMD ["bash"]
