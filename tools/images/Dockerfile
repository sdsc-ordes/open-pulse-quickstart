FROM python:3.10-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.12 /uv /uvx /bin/

# Copy the project into the image
ADD src/ /app/

# make uv's python the default python for the image
ENV PATH="/app/.venv/bin:$PATH"

# Set PYTHONPATH for imports
ENV PYTHONPATH=/app/

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync && uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=open-pulse && uv run --with jupyter jupyter lab

