This is a two-part system designed to process crawled web content (specifically Markdown files) related to museums (in fact, these are just the websites that I crawl for now)!
1.  **Script 1 (Evaluator):** Evaluates the relevance of each Markdown page to museum/art content using an LLM (Ollama) and copies highly relevant pages to a new directory.
2.  **Script 2 (Merger):** Takes the relevant pages from Script 1, merges the content for each museum into a single file, and removes duplicate paragraphs.

The overall goal is to distill a large collection of crawled museum pages into a concise, relevant, and de-duplicated dataset, likely for further processing like creating embeddings or populating a database.
Here's a `README.md` to explain both scripts and their combined workflow:

# Museum Content Processing Pipeline

This project consists of two Python scripts designed to process and refine crawled web content (in Markdown format) related to museums. The pipeline first evaluates the relevance of individual pages using a Large Language Model (LLM) via Ollama, and then merges the content of highly relevant pages, removing duplicates, to create a consolidated information file for each museum.

The ultimate aim is to prepare a clean, relevant, and concise dataset of museum information, suitable for tasks like generating embeddings, populating databases, or further textual analysis.

## Workflow Overview

1.  **Evaluation (Script 1: `evaluate_museum_pages.py`)**:
    *   Scans a directory of crawled museum pages (Markdown files).
    *   For each page, it sends the text content to an Ollama-hosted LLM.
    *   The LLM assigns a relevance score (0-99) based on how pertinent the content is to museums, art, exhibitions, etc.
    *   Pages scoring above a defined threshold are copied to a "pertinent pages" directory, maintaining their original sub-folder structure.
    *   All evaluation scores and statuses are logged to a JSON file.

2.  **Merging & Deduplication (Script 2: `merge_museum_data.py`)**:
    *   Processes the "pertinent pages" directory created by the first script.
    *   For each museum (represented by a sub-folder):
        *   Reads all its Markdown files.
        *   Extracts all paragraphs.
        *   Creates a single new Markdown file for the museum, containing only unique paragraphs from all its source pages, maintaining the order of first appearance.
    *   This results in a de-duplicated, consolidated information file for each museum.

## Scripts

### 1. Museum Page Relevance Evaluator (`evaluate_museum_pages.py`)

This script uses an LLM to assess the relevance of Markdown files concerning museum-related content.

**What it's about:**

This script filters a large collection of crawled web pages (stored as `.md` files) to identify and isolate those that are most relevant to museum and art topics. It automates the process of sifting through potentially noisy crawled data to retain only valuable information.

**Features:**

*   **LLM-based Relevance Scoring:** Leverages an Ollama-hosted LLM (configurable, e.g., `qwen3:30b-a3b`) to score content.
*   **Configurable Parameters:**
    *   Input directory for crawled pages.
    *   Ollama model and host.
    *   Output JSON file for scores.
    *   Maximum text length to send to LLM (to manage context and tokens).
    *   Score threshold for considering a page "pertinent."
    *   Output directory for pertinent pages.
*   **Markdown Text Extraction:** Reads text content from `.md` files.
*   **Robust Score Parsing:** Extracts numerical scores from LLM responses.
*   **Progress Tracking:** Uses `tqdm` for a progress bar during evaluation.
*   **File Copying:** Copies high-scoring files to a separate directory, preserving the original folder structure.
*   **Error Handling:** Includes handling for file operations, Ollama API errors, and encoding issues.

**Prerequisites for this script:**

*   Python 3.x
*   Ollama installed and running.
*   The specified Ollama model (e.g., `qwen3:30b-a3b`) downloaded and available in Ollama.
*   Python libraries: `ollama`, `tqdm`
    ```bash
    pip install ollama tqdm
    ```

**Configuration (Constants in the script):**

*   `MUSEUM_PAGES_DIR`: Path to the parent directory containing sub-folders for each museum with `.md` files.
*   `OLLAMA_MODEL`: Name of the Ollama model to use.
*   `OLLAMA_HOST`: URL of your Ollama server.
*   `OUTPUT_FILE`: Name of the JSON file to save evaluation results.
*   `MAX_TEXT_LENGTH_TO_SEND`: Character limit for text sent to the LLM.
*   `SCORE_THRESHOLD`: Minimum score (0-99) for a page to be copied.
*   `PERTINENT_PAGES_DIR`: Directory where relevant pages will be copied.

**How to Use:**

1.  **Save the script:** e.g., as `evaluate_museum_pages.py`.
2.  **Configure:** Adjust the constants at the top of the script, especially `MUSEUM_PAGES_DIR`, `OLLAMA_MODEL`, `SCORE_THRESHOLD`, and `PERTINENT_PAGES_DIR`.
3.  **Prepare Data:** Ensure your crawled `.md` files are organized in sub-folders (one per museum) within `MUSEUM_PAGES_DIR`.
    Example structure:
    ```
    C:\Users\victo\Desktop\crawl\crawl_output\
    ├── Louvre_Museum\
    │   ├── page1.md
    │   └── page2.md
    └── British_Museum\
        ├── intro.md
        └── exhibits.md
    ```
4.  **Run Ollama:** Make sure your Ollama server is running and the specified model is accessible.
5.  **Execute the script:**
    ```bash
    python evaluate_museum_pages.py
    ```

**Output:**

*   A JSON file (e.g., `scores_evaluation_musees.json`) detailing the score and status for each processed page.
*   A new directory (e.g., `./pages_pertinentes_musees/`) containing copies of the `.md` files that met or exceeded the `SCORE_THRESHOLD`, preserving the original sub-directory structure.

---

### 2. Museum Data Merger (`merge_museum_data.py`)

This script takes the directory of pertinent museum pages (generated by the first script) and consolidates the information for each museum into a single file, removing duplicate paragraphs.

**What it's about:**

After identifying relevant pages, this script aggregates their content. It ensures that the final information for each museum is concise by removing redundant paragraphs that might have appeared across multiple crawled pages of the same museum.

**Features:**

*   **Content Aggregation:** Merges content from multiple `.md` files within each museum's sub-folder.
*   **Paragraph-level Deduplication:** Identifies and retains only unique paragraphs, preserving the order of their first appearance.
*   **Organized Output:** Creates one consolidated `.md` file per museum in a specified output directory.
*   **Encoding Handling:** Attempts to read files with UTF-8 and falls back to Latin-1 if needed.
*   **Clear Logging:** Prints progress and any issues encountered.

**Prerequisites for this script:**

*   Python 3.x
*   Standard Python libraries: `os`, `re`.

**Configuration (Constants/Defaults in the script):**

*   `crawl_museum_dir` (function argument, defaults to `"pages_pertinentes_musees"`): The input directory containing sub-folders of relevant museum pages (output from Script 1).
*   `output_dir` (function argument, defaults to `"musee infos"`): The directory where merged museum files will be saved.

**How to Use:**

1.  **Save the script:** e.g., as `merge_museum_data.py`.
2.  **Ensure Input Data:** Make sure the directory specified by `crawl_museum_dir` (e.g., `pages_pertinentes_musees`) exists and contains the output from the first script.
    Example structure for `pages_pertinentes_musees`:
    ```
    pages_pertinentes_musees/
    ├── Louvre_Museum/
    │   ├── relevant_page1.md
    │   └── relevant_page2.md
    └── British_Museum/
        └── relevant_intro.md
    ```
3.  **Execute the script:**
    ```bash
    python merge_museum_data.py
    ```
    If your input/output directories are different from the defaults, you can modify the call in the `if __name__ == "__main__":` block or pass them as arguments if you adapt the script to accept command-line arguments.

**Output:**

*   A new directory (e.g., `musee infos/`) containing one `.md` file for each museum. Each file will contain:
    *   A title line (e.g., `# Informations du Musée: Louvre_Museum`).
    *   A separator.
    *   All unique paragraphs from the museum's relevant pages, joined by double newlines.
    Example output file: `musee infos/Louvre_Museum.md`

## Running the Full Pipeline

1.  **Setup:**
    *   Install Python.
    *   Install Ollama and download the required LLM model (e.g., `qwen3:30b-a3b`).
    *   Install Python dependencies: `pip install ollama tqdm`.
    *   Save both Python scripts (e.g., `evaluate_museum_pages.py` and `merge_museum_data.py`).
2.  **Prepare Initial Data:**
    *   Create your main input directory for crawled data (e.g., `C:\Users\victo\Desktop\crawl\crawl_output` as per `MUSEUM_PAGES_DIR` in Script 1).
    *   Populate it with sub-directories, one for each museum, containing their respective `.md` files.
3.  **Configure Script 1 (`evaluate_museum_pages.py`):**
    *   Open `evaluate_museum_pages.py` and set the constants like `MUSEUM_PAGES_DIR`, `OLLAMA_MODEL`, `SCORE_THRESHOLD`, and `PERTINENT_PAGES_DIR`.
4.  **Run Script 1:**
    *   Ensure Ollama is running.
    *   Execute: `python evaluate_museum_pages.py`
    *   This will create the `PERTINENT_PAGES_DIR` (e.g., `pages_pertinentes_musees`) and the scores JSON file.
5.  **Configure Script 2 (`merge_museum_data.py`):**
    *   Open `merge_museum_data.py`. The default `crawl_museum_dir="pages_pertinentes_musees"` and `output_dir="musee infos"` should work if you used the default `PERTINENT_PAGES_DIR` in Script 1. Adjust if necessary.
6.  **Run Script 2:**
    *   Execute: `python merge_museum_data.py`
    *   This will create the `output_dir` (e.g., `musee infos`) with the consolidated `.md` files for each museum.

Your final, processed museum data will be in the output directory of Script 2 (e.g., `musee infos`).
