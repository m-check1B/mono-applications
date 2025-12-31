# Lab by Kraliki - Base Dockerfile
# Lab by Kraliki
#
# This Dockerfile builds the base Lab by Kraliki image with all CLI tools pre-installed.
# Used for customer VM deployments.
#
# Build:
#   docker build -t kraliki/magic-box:latest .
#
# Run:
#   docker run -it --rm kraliki/magic-box:latest

FROM ubuntu:24.04

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    vim \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Create magic-box user
RUN useradd -m -s /bin/bash magicbox \
    && usermod -aG sudo magicbox \
    && echo "magicbox ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/magicbox

# Create workspace structure
RUN mkdir -p /opt/magic-box/{config,data,logs,prompts,patterns,scripts} \
    && chown -R magicbox:magicbox /opt/magic-box

# Switch to magic-box user
USER magicbox
WORKDIR /opt/magic-box

# Copy configuration templates
COPY --chown=magicbox:magicbox .env.example /opt/magic-box/config/.env.template

# Set environment
ENV PATH="/opt/magic-box/scripts:${PATH}"
ENV HOME="/home/magicbox"

# Default command
CMD ["/bin/bash"]
