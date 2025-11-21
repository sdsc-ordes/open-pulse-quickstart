FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Set locale to avoid warnings
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install just and other system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    jq \
    && curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash -u 1000 vscode 

USER vscode
WORKDIR /workspaces
