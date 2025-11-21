# QuickStart Neo4J

For open pulse project, you will manipulate graph data with Neo4J. The example notebook will guide you on how to download and visualize the graph. Should you prefer scripts, one is also available to you.

## Working on Renku with Jupyter Notebook 

This set-up provides jupyter notebook support if this is your preferred working method.

Please see instructions in `2025-mini-hackathon.md` at the root of the repository for more instructions.

## Working locally

### 🚀 Part 1: Create the Environment (In Your Terminal)

First, install `uv`. Then, run **all** of the following commands in your system terminal (like Terminal, PowerShell, or bash) from the root folder of the `neo4j-quickstart` project.

**Do not** run these in a notebook cell.

**1. Install `uv` (if not already done):**
Run **one** of these commands in your terminal.

* *On macOS / Linux:*
    ```bash
    curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
    ```
* *On Windows (PowerShell):*
    ```bash
    pip install uv
    ```

> **Note:** After installing, you may need to **restart your terminal or VS Code** for the `uv` command to be recognized.

**2. Create the Environment and Install Packages:**
These commands will create a local `.venv` folder, install all project dependencies (including `ipykernel`), and register it as a named kernel for Jupyter/VS Code.

You can go to `src/neo4j-quickstart` and run `uv sync`.

You can then choose to use a python script or a jupyter notebook.

**3. (if you will use Jupyter Notebooks) Register the Kernel:**
Now, run the command for your operating system to make the new environment visible to Jupyter/VS Code.

* *On macOS / Linux:*
    ```bash
    .venv/bin/python -m ipykernel install --user --name="neo4j-env" --display-name="Python (Neo4j)"
    ```
* *On Windows (PowerShell):*
    ```bash
    .venv\Scripts\python.exe -m ipykernel install --user --name="neo4j-env" --display-name="Python (Neo4j)"
    ```

---

### 💻 Part 2: Run the Code (In VS Code: Script or Notebook)

SCRIPT :

Run the code with `python quickstart.py`

NOTEBOOK :

Now that your environment is built and registered, you can start the notebook.

1.  **Open VS Code:** Open the *entire* `neo4j-quickstart` folder in VS Code (File > Open Folder...).
2.  **Open this Notebook:** Open the `.ipynb` notebook file.
3.  **Select the Kernel:**
    * Click the "Select Kernel" button in the top-right corner of the notebook.
    * From the dropdown list, choose **"Python (Neo4j)"**. This is the name you just registered.
    * If VS Code prompts you, it may also auto-detect the `.venv` folder. Selecting that also works, but the named kernel is more explicit.

You are now ready to run the cells in the notebook.