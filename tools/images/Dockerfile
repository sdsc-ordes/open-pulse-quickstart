FROM python:3.10-slim

# TO-DO how to generalize for other tools. i.e. CHAOSS and a graph database access

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.12 /uv /uvx /bin/

# Copy the project into the image
ADD src/neo4j-quickstart /app/neo4j-quickstart

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN cd neo4j-quickstart && uv sync

# make uv's python the default python for the image
ENV PATH="/app/neo4j-quickstart/.venv/bin:$PATH"

# Set PYTHONPATH for imports
ENV PYTHONPATH=/app/neo4j-quickstart

