# QuickStart Neo4J

For open pulse project, you will manipulate graph data with Neo4J. The example notebook will guide you on how to download and visualize the graph. 

## Working on Renku with Jupyter Notebook 

This set-up provides jupyter notebook support if this is your preferred working method.

Please see instructions in `2025-hackathon.md` at the root of the repository for more instructions.

## Working locally

We are using uv ([installation instructions here](https://docs.astral.sh/uv/getting-started/installation/)).

1. Create virtual environment: `uv venv`
2. Activate it: `source .venv/bin/activate`
3. Get all predefined dependencies from the `uv.lock` file by running the command: `uv sync`
4. Run the code with `python quickstart.py`

Note: uv and Jupyter Notebook integration is not covered in this set-up so you will need to work with python scripts only.

## Build docker

Locally: `docker build -f tools/images/Dockerfile -t neo4j-quickstart .`

Else there is an integrated github CI in the github workflows of this repository.