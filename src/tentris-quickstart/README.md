### 🚀 Part 1: Create the Environment (In Your Terminal)

First, install `uv`. Then, run **all** of the following commands in your system terminal (like Terminal, PowerShell, or bash) from the root folder of the `tentris-quickstart` project.

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

```bash
# 1. Clean up any old environment (optional, but safe)
rm -rf .venv

# 2. Create a new, empty virtual environment
uv venv

# 3. Install all project dependencies from the pyproject.toml file
uv pip install "./src/tentris-quickstart[dev]"
```

**3. Register the Kernel:**
Now, run the command for your operating system to make the new environment visible to Jupyter/VS Code.

* *On macOS / Linux:*
    ```bash
    .venv/bin/python -m ipykernel install --user --name="tentris-env" --display-name="Python (Tentris)"
    ```
* *On Windows (PowerShell):*
    ```bash
    .venv\Scripts\python.exe -m ipykernel install --user --name="tentris-env" --display-name="Python (Tentris)"
    ```

---

### 💻 Part 2: Run the Notebook (In VS Code)

Now that your environment is built and registered, you can start the notebook.

1.  **Open VS Code:** Open the *entire* `tentris-quickstart` folder in VS Code (File > Open Folder...).
2.  **Open this Notebook:** Open the `.ipynb` notebook file.
3.  **Select the Kernel:**
    * Click the "Select Kernel" button in the top-right corner of the notebook.
    * From the dropdown list, choose **"Python (Tentris)"**. This is the name you just registered.
    * If VS Code prompts you, it may also auto-detect the `.venv` folder. Selecting that also works, but the named kernel is more explicit.

You are now ready to run the cells in the notebook.